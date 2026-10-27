import unittest
from scripts.observe_products import inspect

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

if __name__ == "__main__":
    unittest.main()
