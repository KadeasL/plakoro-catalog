import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sitemap import discover

class SitemapTests(unittest.TestCase):
    def test_matching_same_host_only(self):
        xml = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
               '<url><loc>https://example.jp/plakoro/01</loc></url>'
               '<url><loc>https://other.jp/plakoro/02</loc></url>'
               '<url><loc>https://example.jp/other</loc></url></urlset>')
        rows = discover(xml, "https://example.jp/sitemap.xml")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "needs_review")
    def test_invalid_xml_type(self):
        with self.assertRaises(ValueError):
            discover("<hello/>", "https://example.jp/sitemap.xml")
if __name__ == "__main__":
    unittest.main()
