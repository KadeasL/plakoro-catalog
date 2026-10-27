#!/usr/bin/env python3
"""Inspect explicitly registered product pages; observations are NOT sale confirmations."""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
from scripts.product_status import classify

ROOT = Path(__file__).resolve().parents[1]
WATCHLIST = ROOT / "catalog/product_watchlist.json"
REPORT = ROOT / "catalog/product_observations.json"
MAX_BYTES = 1_000_000

def inspect(item, fetch=None):
    """Fail closed when the item, URL or status-specific text is not trustworthy."""
    required = ("id", "name_ja", "release_date", "product_url", "name_marker")
    if any(not item.get(k) for k in required):
        return {"id": item.get("id"), "status": "unknown", "reason": "missing required metadata"}
    url = item["product_url"]
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return {"id": item["id"], "status": "unknown", "reason": "invalid HTTPS URL"}
    if fetch is None:
        def fetch(url):
            request = urllib.request.Request(url, headers={"User-Agent": "PlakoroCatalogResearch/0.3"})
            with urllib.request.urlopen(request, timeout=15) as response:
                final = urlparse(response.geturl())
                if final.scheme != "https" or final.hostname != parsed.hostname:
                    raise ValueError("redirected away from expected retailer")
                return response.read(MAX_BYTES).decode("utf-8", "replace")
    try:
        raw = fetch(url)
        if item["name_marker"] not in unescape(raw):
            return {"id": item["id"], "status": "unknown", "reason": "product identity not found"}
        # Product-specific selector is required. Whole-page buttons may belong to recommendations.
        pattern = item.get("stock_pattern")
        if not pattern:
            return {"id": item["id"], "status": "unknown", "reason": "stock selector not configured"}
        match = re.search(pattern, raw, flags=re.I | re.S)
        if not match or "status" not in match.groupdict():
            return {"id": item["id"], "status": "unknown", "reason": "stock selector not matched"}
        status_text = re.sub(r"<[^>]*>", " ", unescape(match.group("status")))
        status, reason = classify(item["name_ja"], status_text, item["release_date"])
        return {"id": item["id"], "status": status, "reason": reason,
                "product_url": url, "stock_text": status_text.strip()[:160]}
    except Exception as exc:
        return {"id": item["id"], "status": "unknown", "reason": "fetch error: " + str(exc)[:160]}

def inspect_official(item, fetch=None):
    """Check the official Bandai page identity; never infer retailer availability."""
    url = item.get("official_url")
    if not url:
        return {"status": "unknown", "reason": "official URL missing"}
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "bandai-hobby.net":
        return {"status": "unknown", "reason": "untrusted official URL"}
    if fetch is None:
        def fetch(target):
            request = urllib.request.Request(target, headers={"User-Agent": "Mozilla/5.0 PlakoroCatalogResearch/0.4"})
            with urllib.request.urlopen(request, timeout=12) as response:
                final = urlparse(response.geturl())
                if final.scheme != "https" or final.hostname != parsed.hostname:
                    raise ValueError("official page redirected outside domain")
                return response.read(MAX_BYTES).decode("utf-8", "replace")
    try:
        raw = unescape(fetch(url))
        marker = item.get("name_marker", "")
        if not marker or marker not in raw:
            return {"status": "unknown", "reason": "official product identity not matched"}
        return {"status": "identity_matched", "reason": "official product page identified; not proof of stock"}
    except Exception as exc:
        return {"status": "unknown", "reason": "official fetch error: " + str(exc)[:160]}

def main():
    data = json.loads(WATCHLIST.read_text(encoding="utf-8"))
    items = data.get("products", [])
    if not isinstance(items, list):
        raise ValueError("products must be a list")
    if not items:
        raise RuntimeError("Watchlist is empty: refusing a misleading successful monitoring run")
    observations = [inspect(item) for item in items]
    for item, observation in zip(items, observations):
        observation["official_url"] = item.get("official_url")
        observation["official_release_date"] = item.get("release_date") if item.get("release_date_precision") == "day" else None
        observation["official_price_jpy"] = item.get("official_price_jpy")
        observation["retailer_url"] = item.get("product_url")
        observation["official_page_check"] = inspect_official(item)
        observation["verified_for_email"] = False
    REPORT.write_text(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(),
       "observations": observations,
       "note": "Candidates require independent verification; this report never sends mail."},
       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Watched products:", len(items), "candidate signals:",
          sum(x["status"] == "candidate_in_stock" for x in observations))
    if not items:
        print("Watchlist empty: add independently verified product URLs before monitoring.")

if __name__ == "__main__":
    main()
