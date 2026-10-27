#!/usr/bin/env python3
"""Conservative discovery of Plakoro retailer listing changes; never email automatically."""
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "catalog" / "retailer_observations.json"
SOURCES = [
    ("hobbysearch", "https://www.1999.co.jp/mlist/765/2/1/"),
    ("yodobashi", "https://www.yodobashi.com/category/141001/141336/141538/141539/m5000002032/"),
    ("joshin", "https://joshinweb.jp/watch/4091/?LVC=100&LVT=0&PGN=24&SRT=8"),
]
KEYWORD = re.compile(r"プラコロ")
PRODUCT = re.compile(r"(?:スタートセット|たんけんボックス|進化セット|テラスタル|DXスタートセット|DXケース)")
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "PlakoroReleaseMonitor/0.1 (research; contact via GitHub)"})
    with urllib.request.urlopen(req, timeout=20) as res:
        if res.status != 200:
            raise RuntimeError("Unexpected HTTP status")
        return res.read(2_000_000).decode("utf-8", "replace")
def clean(page):
    page = re.sub(r"<(script|style)\\b[^>]*>.*?</\\1>", " ", page, flags=re.I|re.S)
    page = re.sub(r"<[^>]+>", " ", page)
    return re.sub(r"\\s+", " ", html.unescape(page))
def main():
    observations, errors = [], []
    for name, url in SOURCES:
        try:
            body = clean(get(url))
            # Listing-level observations only; not product-specific availability evidence.
            matches = [body[max(0,m.start()-50):m.start()+140] for m in KEYWORD.finditer(body)]
            observations.append({"source": name, "url": url,
                                 "listing_accessible": True,
                                 "mentions": [m for m in matches if PRODUCT.search(m)][:100]})
        except Exception as exc:
            errors.append({"source": name, "error": str(exc)})
    OUT.write_text(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(),
                              "observations": observations, "errors": errors,
                              "warning": "Listing text is not proof of sale. Human/product-page verification required."},
                             ensure_ascii=False, indent=2)+"\\n", encoding="utf-8")
    print("Checked sources:", len(observations), "errors:", len(errors))
if __name__ == "__main__":
    main()
