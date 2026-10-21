#!/usr/bin/env python3
"""Find release candidates in explicitly configured RSS/Atom feeds; never auto-publish."""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from translate import enrich_candidate

ROOT = Path(__file__).resolve().parents[1]
KEYWORDS = re.compile(r"plakoro|プラコロ|ポケモン.*(ボックス|セット)", re.I)
ATOM = "{http://www.w3.org/2005/Atom}"

def fetch(url):
    if not url.startswith("https://"):
        raise ValueError("Only HTTPS feeds are allowed")
    request = urllib.request.Request(url, headers={"User-Agent": "PlakoroCatalogResearch/0.1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read(2_000_000).decode("utf-8", errors="replace")

def parse(content, source):
    root = ET.fromstring(content)
    entries = []
    for e in root.findall(".//item"):
        entries.append((e.findtext("title", ""), e.findtext("link", ""), e.findtext("pubDate", "")))
    for e in root.findall(f".//{ATOM}entry"):
        links = e.findall(f"{ATOM}link")
        link = next((x.get("href", "") for x in links if x.get("rel", "alternate") == "alternate"), "")
        entries.append((e.findtext(f"{ATOM}title", ""), link, e.findtext(f"{ATOM}updated", "")))
    return [{"title": t.strip(), "url": u.strip(), "published": d, "source_feed": source, "status": "needs_review"}
            for t, u, d in entries if KEYWORDS.search(t) and u.startswith("https://")]

def main():
    config = json.loads((ROOT / "sources/feeds.json").read_text(encoding="utf-8"))
    candidates, errors, seen = [], [], set()
    for feed in config.get("feeds", []):
        if not feed.get("enabled", True):
            continue
        url = feed.get("url", "")
        try:
            for candidate in parse(fetch(url), url):
                if candidate["url"] not in seen:
                    candidates.append(enrich_candidate(candidate))
                    seen.add(candidate["url"])
        except Exception as exc:
            errors.append({"feed": url, "error": str(exc)})
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "configured_feeds": len(config.get("feeds", [])),
              "candidates": candidates, "errors": errors}
    (ROOT / "candidates.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Candidates: {len(candidates)}, errors: {len(errors)}")
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
