from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
import os
import sys
import subprocess
import base64
import asyncio
import concurrent.futures
import threading
import uuid
import logging
import shutil
import time
from pathlib import Path as Pathlib
from collections import OrderedDict
from typing import List


app = FastAPI(title="Lembrent + Glyphs API")

# Project layout
# filesystem helpers
PROJECT_ROOT = Pathlib(__file__).resolve().parents[1]
LEMBRENT_PATH = PROJECT_ROOT / "lembrent" / "lembrent"

# Cache configuration (env override)
DISK_CACHE_DIR = Pathlib(os.getenv("DISK_CACHE_DIR", PROJECT_ROOT / "api" / "cache")).resolve()
MAX_CACHE_ENTRIES = int(os.getenv("MAX_CACHE_ENTRIES", "2048"))
API_MAX_WORKERS = int(os.getenv("API_MAX_WORKERS", "8"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "0"))  # 0 => no TTL
KEEP_CACHE_VERSIONS = int(os.getenv("KEEP_CACHE_VERSIONS", "3"))
MAX_CACHE_AGE_DAYS = int(os.getenv("MAX_CACHE_AGE_DAYS", "30"))


class LRUCache:
    def __init__(self, maxsize: int = 2048):
        self.maxsize = int(maxsize)
        self.lock = threading.Lock()
        self.data = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        with self.lock:
            if key in self.data:
                val = self.data.pop(key)
                # move to end
                self.data[key] = val
                self.hits += 1
                return val
            self.misses += 1
            return None

    def set(self, key, value):
        with self.lock:
            if key in self.data:
                self.data.pop(key)
            self.data[key] = value
            if len(self.data) > self.maxsize:
                self.data.popitem(last=False)

    def stats(self):
        with self.lock:
            return {"size": len(self.data), "maxsize": self.maxsize, "hits": self.hits, "misses": self.misses}

    def clear(self):
        with self.lock:
            self.data.clear()
            self.hits = 0
            self.misses = 0


def compute_cache_version() -> str:
    # Prefer git short SHA if available, else fallback to mtimes
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(PROJECT_ROOT))
        return out.decode().strip()
    except Exception:
        mtimes = []
        glyphs_src = PROJECT_ROOT / "glyphs" / "src"
        lemb = PROJECT_ROOT / "lembrent" / "lembrent"
        for p in (glyphs_src, lemb):
            if p.exists():
                if p.is_file():
                    mtimes.append(int(p.stat().st_mtime))
                else:
                    for f in p.rglob("*"):
                        if f.is_file():
                            mtimes.append(int(f.stat().st_mtime))
        if mtimes:
            return "mtime-" + str(max(mtimes))
        return "nocacheversion"


# Current cache version (may change during runtime)
CURRENT_CACHE_VERSION = compute_cache_version()

def get_cache_base() -> Pathlib:
    return DISK_CACHE_DIR / CURRENT_CACHE_VERSION

# Ensure cache base exists
get_cache_base().mkdir(parents=True, exist_ok=True)

# In-memory cache
mem_cache = LRUCache(MAX_CACHE_ENTRIES)

# Logging
logger = logging.getLogger(__name__)
cache_version_lock = threading.Lock()


def check_and_invalidate_cache():
    """Recompute cache version; if it changed, clear in-memory cache and switch cache base."""
    global CURRENT_CACHE_VERSION
    try:
        new_version = compute_cache_version()
    except Exception:
        return
    with cache_version_lock:
        if new_version != CURRENT_CACHE_VERSION:
            logger.info(f"Cache version changed: {CURRENT_CACHE_VERSION} -> {new_version}; clearing caches")
            try:
                mem_cache.clear()
            except Exception:
                pass
            CURRENT_CACHE_VERSION = new_version
            try:
                get_cache_base().mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            # prune old cache dirs asynchronously
            try:
                executor.submit(prune_old_cache_dirs)
            except Exception:
                # executor may not be ready during early init; ignore
                pass

# Thread pool for blocking IO
executor = concurrent.futures.ThreadPoolExecutor(max_workers=API_MAX_WORKERS)


def to_base_digits(number: int, radix: int) -> List[int]:
    if number == 0:
        return [0]
    digits = []
    n = int(number)
    while n > 0:
        digits.append(n % radix)
        n //= radix
    return digits[::-1]


def disk_cache_path(radix: int, digit: int, typ: str, clean: bool = True, force: bool = True) -> Pathlib:
    subdir = get_cache_base() / str(radix)
    subdir.mkdir(parents=True, exist_ok=True)
    flags = f"c{int(bool(clean))}_f{int(bool(force))}"
    filename = f"{digit}.{typ}.{flags}"
    return subdir / filename


def prune_old_cache_dirs(keep: int = KEEP_CACHE_VERSIONS, max_age_days: int = MAX_CACHE_AGE_DAYS):
    """Prune old cache version directories under DISK_CACHE_DIR, keeping at most `keep` latest directories and removing directories older than `max_age_days` days.

    This is safe-limited to subdirectories of DISK_CACHE_DIR.
    """
    base = Pathlib(DISK_CACHE_DIR)
    if not base.exists():
        return
    try:
        entries = [p for p in base.iterdir() if p.is_dir()]
    except Exception:
        return
    if not entries:
        return
    # sort by modification time (newest first)
    entries_sorted = sorted(entries, key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    current_name = get_cache_base().name
    # names to keep: newest `keep` plus the current cache
    keep_names = set(p.name for p in entries_sorted[:max(keep, 0)])
    keep_names.add(current_name)
    now = time.time()
    cutoff = now - (max_age_days * 86400) if max_age_days and max_age_days > 0 else None
    for p in entries_sorted:
        if p.name in keep_names:
            continue
        try:
            if cutoff is not None:
                try:
                    mtime = p.stat().st_mtime
                except Exception:
                    mtime = 0
                if mtime > cutoff:
                    # not old enough to prune
                    continue
            # delete
            shutil.rmtree(p)
            logger.info(f"Pruned old cache directory {p}")
        except Exception as e:
            logger.warning(f"Failed to prune cache dir {p}: {e}")


def read_disk_cache(path: Pathlib, binary: bool):
    try:
        if not path.exists():
            return None
        mode = "rb" if binary else "r"
        with path.open(mode) as f:
            return f.read()
    except Exception:
        return None


def write_disk_cache(path: Pathlib, data, binary: bool):
    try:
        tmp = path.parent / (path.name + ".tmp-" + uuid.uuid4().hex)
        tmp.parent.mkdir(parents=True, exist_ok=True)
        mode = "wb" if binary else "w"
        with tmp.open(mode) as f:
            f.write(data)
        # atomic replace
        os.replace(str(tmp), str(path))
    except Exception:
        # best-effort cache write; do not fail the request
        pass


def generate_svg_subprocess(radix: int, digit: int, clean: bool = True, force: bool = True, timeout: int = 10) -> str:
    cmd = [sys.executable, "-m", "glyphs"]
    if clean:
        cmd.append("--clean")
    if force:
        cmd.append("--force")
    cmd += ["--scheme", str(radix), "--digit", str(digit), "--svg", "-"]
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if proc.returncode != 0:
        stderr = proc.stderr.decode(errors="ignore") if proc.stderr else ""
        raise RuntimeError(f"glyphs svg generation failed: {stderr}")
    return proc.stdout.decode(errors="ignore")


def generate_png_subprocess(radix: int, digit: int, clean: bool = True, force: bool = True, timeout: int = 10) -> bytes:
    cmd = [sys.executable, "-m", "glyphs"]
    if clean:
        cmd.append("--clean")
    if force:
        cmd.append("--force")
    cmd += ["--scheme", str(radix), "--digit", str(digit), "--png", "-"]
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if proc.returncode != 0:
        stderr = proc.stderr.decode(errors="ignore") if proc.stderr else ""
        raise RuntimeError(f"glyphs png generation failed: {stderr}")
    return proc.stdout


def get_svg_cached(radix: int, digit: int, clean: bool = True, force: bool = True) -> str:
    key = ("svg", radix, digit, bool(clean), bool(force))
    val = mem_cache.get(key)
    if val is not None:
        return val
    path = disk_cache_path(radix, digit, "svg", clean, force)
    data = read_disk_cache(path, binary=False)
    if data is not None:
        mem_cache.set(key, data)
        return data
    # generate
    data = generate_svg_subprocess(radix, digit, clean, force)
    try:
        write_disk_cache(path, data, binary=False)
    except Exception:
        pass
    mem_cache.set(key, data)
    return data


def get_png_cached(radix: int, digit: int, clean: bool = True, force: bool = True) -> bytes:
    key = ("png", radix, digit, bool(clean), bool(force))
    val = mem_cache.get(key)
    if val is not None:
        return val
    path = disk_cache_path(radix, digit, "png", clean, force)
    data = read_disk_cache(path, binary=True)
    if data is not None:
        mem_cache.set(key, data)
        return data
    # generate
    data = generate_png_subprocess(radix, digit, clean, force)
    try:
        write_disk_cache(path, data, binary=True)
    except Exception:
        pass
    mem_cache.set(key, data)
    return data


def run_lembrent_subprocess(radix: int, number: int, timeout: int = 5) -> str:
    if not LEMBRENT_PATH.exists():
        raise RuntimeError("lembrent script not found in repository")
    proc = subprocess.run([str(LEMBRENT_PATH), str(radix), str(number)], cwd=str(PROJECT_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if proc.returncode != 0:
        stderr = proc.stderr.decode(errors="ignore") if proc.stderr else ""
        raise RuntimeError(f"lembrent failed: {stderr}")
    return proc.stdout.decode(errors="ignore").strip()


@app.get("/lembrent/{radix}/{number}")
async def lembent_endpoint(
    radix: int = Path(..., description="60 or 64"),
    number: int = Path(..., description="non-negative integer"),
    name: int = Query(1, ge=0, le=1),
    svg: int = Query(1, ge=0, le=1),
    png: int = Query(0, ge=0, le=1),
):
    # Convert flags
    want_name = bool(int(name))
    want_svg = bool(int(svg))
    want_png = bool(int(png))

    # Invalidate cache if source files changed since last check
    check_and_invalidate_cache()

    if radix not in (60, 64):
        raise HTTPException(status_code=400, detail="radix must be 60 or 64")
    if number < 0:
        raise HTTPException(status_code=400, detail="number must be non-negative")

    digits = to_base_digits(number, radix)
    loop = asyncio.get_event_loop()

    try:
        # gather name
        result = {}
        if want_name:
            name_future = loop.run_in_executor(executor, run_lembrent_subprocess, radix, number)
            name_value = await name_future
            result["name"] = name_value

        # gather svg/png concurrently per digit
        if want_svg:
            svg_futures = [loop.run_in_executor(executor, get_svg_cached, radix, d, True, True) for d in digits]
            svg_vals = await asyncio.gather(*svg_futures)
            result["svg"] = svg_vals

        if want_png:
            png_futures = [loop.run_in_executor(executor, get_png_cached, radix, d, True, True) for d in digits]
            png_vals = await asyncio.gather(*png_futures)
            # base64-encode
            result["png"] = [base64.b64encode(b).decode() for b in png_vals]

        return JSONResponse(content=result)

    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="generation timed out")


@app.get("/metrics")
def metrics():
    return mem_cache.stats()


@app.on_event("startup")
def on_startup():
    # Ensure cache version is current and perform an initial prune asynchronously
    try:
        check_and_invalidate_cache()
    except Exception:
        pass
    try:
        executor.submit(prune_old_cache_dirs)
    except Exception:
        pass
