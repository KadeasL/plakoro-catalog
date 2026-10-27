#!/usr/bin/env python3
"""Monitor retailer listing pages; evidence only, not proof of a completed release."""
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "catalog" / "retailer_observations.json"
SOURCES = [
    ("hobbysearch", "https://www.1999.co.jp/mlist/765/7/1"),
    ("yodobashi", "https://www.yodobashi.com/category/141001/141336/141538/141539/m5000002032/"),
    ("pokemon_center", "https://www.pokemoncenter-online.com/4580886846931.html"),
]
KEYWORD = re.compile("プラコロ", re.I)
PRODUCT = re.compile("スタートセット|たんけんボックス|進化セット|テラスタル|DX")
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; PlakoroCatalogResearch/0.2)"})
    with urllib.request.urlopen(req, timeout=20) as res:
        if res.status != 200:
            raise RuntimeError("Unexpected HTTP status")
        return res.read(2_000_000).decode("utf-8", "replace")
def clean(page):
    page = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", page, flags=re.I|re.S)
    page = re.sub(r"<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(page))
def main():
    observations, errors = [], []
    for name, url in SOURCES:
        try:
            body = clean(get(url))
            matches = [body[max(0,m.start()-40):m.start()+170] for m in KEYWORD.finditer(body)]
            observations.append({"source": name, "url": url,
                                 "listing_accessible": True,
                                 "mentions": [m for m in matches if PRODUCT.search(m)][:100]})
        except Exception as exc:
            errors.append({"source": name, "error": str(exc)})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(),
                              "observations": observations, "errors": errors,
                              "warning": "Listing text is not proof of sale. Product-page verification required."},
                             ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Checked sources:", len(observations), "errors:", len(errors))
    for error in errors:
        print("SOURCE ERROR:", error["source"], error["error"])
    if not observations:
        raise SystemExit("No retailer sources accessible; observations incomplete")
if __name__ == "__main__":
    main()
