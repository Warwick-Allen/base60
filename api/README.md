# Lembrent + Glyphs API

This small FastAPI application exposes a single endpoint:

- `GET /lembrent/{radix}/{number}`

Query parameters (defaults):
- `name=1` (include lembrenet name)
- `svg=1` (include per-digit SVG strings)
- `png=0` (include per-digit PNGs as base64)

Run locally (install dependencies first):

```bash
pip install -r api/requirements.txt
uvicorn api.app:app --reload --port 8000
```

Examples:

```bash
curl -s "http://127.0.0.1:8000/lembrent/60/70?name=1&svg=1&png=0"
curl -s "http://127.0.0.1:8000/lembrent/64/12?name=1&svg=1&png=1" | jq .
```

Cache
- In-memory LRU cache (config via `MAX_CACHE_ENTRIES`)
- Optional disk cache stored under `api/cache/{cache_version}` (configurable via `DISK_CACHE_DIR`)
