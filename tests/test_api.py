import base64
from fastapi.testclient import TestClient

import api.app as app_module

client = TestClient(app_module.app)


def test_name_only(monkeypatch):
    def fake_lembrent(radix, number, timeout=5):
        return "seen-eet"

    monkeypatch.setattr(app_module, "run_lembrent_subprocess", fake_lembrent)

    res = client.get("/lembrent/60/70?name=1&svg=0&png=0")
    assert res.status_code == 200
    assert res.json().get("name") == "seen-eet"


def test_svg_png(monkeypatch):
    def fake_get_svg(radix, digit, clean=True, force=True):
        return f"<svg>{radix}-{digit}</svg>"

    def fake_get_png(radix, digit, clean=True, force=True):
        return f"PNG{radix}{digit}".encode("utf-8")

    monkeypatch.setattr(app_module, "get_svg_cached", fake_get_svg)
    monkeypatch.setattr(app_module, "get_png_cached", fake_get_png)

    # number 62 in base 60 -> digits [1, 2]
    res = client.get("/lembrent/60/62?name=0&svg=1&png=1")
    assert res.status_code == 200
    data = res.json()
    assert "svg" in data and len(data["svg"]) == 2
    assert data["svg"][0] == "<svg>60-1</svg>"
    assert "png" in data and len(data["png"]) == 2
    assert base64.b64decode(data["png"][0]) == b"PNG601"


def test_invalid_radix():
    res = client.get("/lembrent/61/10")
    assert res.status_code == 400
