import unittest
from scripts.sale_status import classify

class SaleStatusTests(unittest.TestCase):
    def test_preorder_overrides_cart(self):
        self.assertEqual(classify("予約受付中 カートに入れる", product_page=True)[0], "preorder")
    def test_sold_out_overrides_cart(self):
        self.assertEqual(classify("売り切れ カートに入れる", product_page=True)[0], "out_of_stock")
    def test_listing_never_proves_stock(self):
        self.assertEqual(classify("在庫あり", product_page=False)[0], "unknown")
    def test_stock_requires_review(self):
        self.assertEqual(classify("在庫あり", product_page=True)[0], "possible_in_stock")
    def test_release_date_is_not_stock(self):
        self.assertEqual(classify("2026年11月発売", product_page=True)[0], "unknown")

if __name__ == "__main__":
    unittest.main()
