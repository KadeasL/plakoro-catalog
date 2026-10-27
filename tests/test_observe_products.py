import unittest
from scripts.observe_products import inspect, inspect_official

ITEM = {"id": "test", "name_ja": "プラコロ スタートセット カイリュー",
        "release_date": "2026-10-20", "product_url": "https://example.jp/product/1",
        "name_marker": "カイリュー", "stock_pattern": r'<div id="stock">(?P<status>.*?)</div>'}

class ProductObservationTests(unittest.TestCase):
    def test_explicit_stock_is_candidate(self):
        self.assertEqual(inspect(ITEM, lambda url: '<h1>カイリュー</h1><div id="stock">在庫あり</div>')["status"], "candidate_in_stock")
    def test_preorder_is_not_sale(self):
        self.assertEqual(inspect(ITEM, lambda url: '<h1>カイリュー</h1><div id="stock">予約受付中</div>')["status"], "not_available")
    def test_unrelated_page_is_unknown(self):
        self.assertEqual(inspect(ITEM, lambda url: '<div id="stock">在庫あり</div>')["status"], "unknown")
    def test_missing_selector_is_unknown(self):
        self.assertEqual(inspect({k:v for k,v in ITEM.items() if k!="stock_pattern"}, lambda url: 'カイリュー 在庫あり')["status"], "unknown")
    def test_future_release_is_not_sale(self):
        item = dict(ITEM, release_date="2099-11-20")
        self.assertEqual(inspect(item, lambda url: 'カイリュー<div id="stock">在庫あり</div>')["status"], "not_available")

class OfficialPageTests(unittest.TestCase):
    def test_matching_official_page_is_not_stock_confirmation(self):
        item = dict(ITEM, official_url="https://bandai-hobby.net/item/01_7184/")
        result = inspect_official(item, lambda url: "<h1>プラコロ スタートセット カイリュー 11</h1>")
        self.assertEqual(result["status"], "identity_matched")
        self.assertNotIn("candidate_in_stock", str(result))
    def test_untrusted_official_domain_is_rejected(self):
        item = dict(ITEM, official_url="https://example.jp/item/01_7184/")
        self.assertEqual(inspect_official(item, lambda url: "カイリュー")["status"], "unknown")
    def test_missing_identity_fails_closed(self):
        item = dict(ITEM, official_url="https://bandai-hobby.net/item/01_7184/")
        self.assertEqual(inspect_official(item, lambda url: "another product")["status"], "unknown")

if __name__ == "__main__":
    unittest.main()
