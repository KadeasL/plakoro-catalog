"""Discover candidate URLs from explicitly configured XML sitemaps.

Sitemap entries are leads only: they are not verified release records.
"""
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from urllib.request import Request, urlopen

PATTERN = re.compile(r"plakoro|プラコロ|pokemon|ポケモン", re.I)
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
USER_AGENT = "PlakoroCatalogResearch/0.2"

def discover(xml_text, sitemap_url, limit=200):
    root = ET.fromstring(xml_text)
    if root.tag != NS + "urlset":
        raise ValueError("Expected sitemap urlset; sitemap indexes need explicit configuration")
    found = []
    host = urlparse(sitemap_url).hostname
    for entry in root.findall(NS + "url")[:limit]:
        url = (entry.findtext(NS + "loc") or "").strip()
        parsed = urlparse(url)
        if parsed.scheme == "https" and parsed.hostname == host and PATTERN.search(url):
            found.append({"title": None, "url": url, "published": None,
                          "source_feed": sitemap_url, "status": "needs_review",
                          "discovery_method": "sitemap_url"})
    return found

def fetch_sitemap(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Sitemap must use HTTPS")
    robots_url = f"https://{parsed.hostname}/robots.txt"
    robots = RobotFileParser()
    robots.set_url(robots_url)
    try:
        robots.read()
    except Exception as exc:
        raise RuntimeError("Cannot verify robots.txt; skipping sitemap") from exc
    if not robots.can_fetch(USER_AGENT, url):
        raise PermissionError("robots.txt disallows sitemap fetch")
    with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=20) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Sitemap too large")
    return data.decode("utf-8", errors="replace")
