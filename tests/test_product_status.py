import unittest
from datetime import date
from scripts.product_status import classify

TODAY = date(2026, 10, 27)
NAME = "プラコロ スタートセット カイリュー 11"
class ProductStatusTests(unittest.TestCase):
    def check(self, name, status, day, expected):
        self.assertEqual(classify(name, status, day, TODAY)[0], expected)
    def test_preorder_overrides_purchase(self):
        self.check(NAME, "予約受付中 カートに入れる", "2026-11-21", "not_available")
    def test_future_date_overrides_stock(self):
        self.check(NAME, "在庫あり", "2026-11-21", "not_available")
    def test_sold_out_overrides_sale(self):
        self.check(NAME, "品切れ 販売中", "2026-10-24", "not_available")
    def test_restock_not_new_release(self):
        self.check(NAME+" 再入荷", "在庫あり", "2026-10-24", "ignore")
    def test_old_product_only_candidate(self):
        self.check(NAME, "在庫あり カートに入れる", "2026-10-24", "candidate_in_stock")
    def test_no_date(self):
        self.check(NAME, "在庫あり", None, "unknown")
    def test_no_stock_signal(self):
        self.check(NAME, "商品情報", "2026-10-24", "unknown")
    def test_unrelated(self):
        self.check("GUNDAM STARTER SET", "在庫あり", "2026-10-24", "ignore")
if __name__ == "__main__":
    unittest.main()
