"""Conservative Japanese retailer availability classifier.

Only evaluates text from a known product page. A listing page or ambiguous text
is never proof of stock. A positive signal requires explicit purchase status.
"""
import re

OUT_OF_STOCK = ("在庫なし", "在庫切れ", "売り切れ", "売切れ", "品切れ", "販売終了", "完売", "入荷待ち", "お取り寄せ", "取扱終了")
PREORDER = ("予約受付中", "予約商品", "予約受付", "予約開始", "予約販売", "予約注文", "発売予定", "発売前", "近日発売", "予約締切")
IN_STOCK = ("在庫あり", "在庫有り", "在庫有", "在庫：あり", "在庫:あり", "カートに入れる", "カートに追加", "購入する")
def classify(text, *, product_page=False):
    """Return (status, reason); never claim stock without a product-page signal."""
    if not product_page:
        return "unknown", "not_a_product_page"
    text = re.sub(r"\\s+", "", text)
    if any(word in text for word in PREORDER):
        return "preorder", "preorder_signal"
    if any(word in text for word in OUT_OF_STOCK):
        return "out_of_stock", "unavailable_signal"
    if any(word in text for word in IN_STOCK):
        return "possible_in_stock", "purchase_signal_requires_review"
    return "unknown", "no_explicit_purchase_signal"
