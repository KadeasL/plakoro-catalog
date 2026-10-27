#!/usr/bin/env python3
"""Collect retailer evidence. NEVER treat this report as authorization to email."""
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "catalog" / "retailer_observations.json"
SOURCES = [
    ("pokemon_center", "https://www.pokemoncenter-online.com/4580886846931.html"),
    ("bandai_official", "https://www.bandaispirits.co.jp/products/search/detail.php?grp_id=5325&prd_id=4573102722003000"),
]
PREORDER = ("予約受付中", "予約商品", "予約受付を終了", "発売予定", "再販予約", "予約受付終了")
OUT_OF_STOCK = ("品切れ", "在庫なし", "売り切れ", "販売休止中", "販売終了", "完売")
IN_STOCK = ("在庫あり", "カートに入れる", "購入する", "販売中")
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; PlakoroCatalogResearch/0.3)"})
    with urllib.request.urlopen(req, timeout=20) as res:
        if res.status != 200:
            raise RuntimeError("Unexpected HTTP status")
        raw = res.read(2_000_000)
        charset = res.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, "replace")
def clean(page):
    page = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", page, flags=re.I|re.S)
    page = re.sub(r"<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(page))
def classify(text):
    # Whole-page status signals can refer to other products: evidence only.
    if any(t in text for t in PREORDER):
        return "preorder_or_ambiguous"
    if any(t in text for t in OUT_OF_STOCK):
        return "out_of_stock_or_ambiguous"
    if any(t in text for t in IN_STOCK):
        return "possible_in_stock_unverified"
    return "unknown"
def main():
    observations, errors = [], []
    for name, url in SOURCES:
        try:
            page = clean(fetch(url))
            mentions = [page[max(0, m.start()-60):m.start()+180] for m in re.finditer("プラコロ", page)]
            observations.append({"source": name, "url": url, "listing_accessible": True,
                                 "mentions": mentions[:30], "page_status": classify(page),
                                 "has_plakoro": bool(mentions), "verified_for_email": False})
        except Exception as exc:
            errors.append({"source": name, "error": str(exc)})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(),
                              "observations": observations, "errors": errors,
                              "warning": "No stock status here is verified for email. Never auto-promote these observations."},
                             ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Sources accessible:", len(observations), "errors:", len(errors))
    for error in errors:
        print("SOURCE ERROR:", error["source"], error["error"])
    if not observations or not any(x["has_plakoro"] for x in observations):
        raise SystemExit("No usable Plakoro observations: investigation needed")
if __name__ == "__main__":
    main()
