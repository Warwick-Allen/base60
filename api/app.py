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

# --- Static files serving ---
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Lembrent + Glyphs API")

# Serve static files (e.g. HTML, JS, CSS) from the 'static' dir at root path
STATIC_DIR = Pathlib(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

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

# ...rest of code remains unchanged: all API endpoints etc ...

# [The rest of your app.py follows here unchanged]
