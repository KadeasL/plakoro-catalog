#!/usr/bin/env python3
"""Conservative Japanese Plakoro stock classifier.

Only product-specific text is eligible. Listing snippets, preorders, and
restocks are not evidence of a new release. No mail is sent by this module.
"""
import re
from datetime import date

POSITIVE = ("在庫あり", "販売中", "カートに入れる", "購入する")
NEGATIVE = ("予約受付中", "予約品", "予約商品", "予約受付", "発売予定",
            "在庫なし", "品切れ", "売り切れ", "販売終了", "注文停止",
            "オーダーストップ", "再入荷通知", "お取り寄せ", "入荷待ち")
REPRINT = ("再販", "再入荷")
RELEASE = ("スタートセット", "たんけんボックス", "進化セット",
           "DXスタートセット", "テラスタル")

def classify(name, status_text, release_date=None, today=None):
    """Return status, reason. Requires retailer product-level status text."""
    today = today or date.today()
    if not any(term in name for term in RELEASE) or "プラコロ" not in name:
        return "ignore", "not a Plakoro set"
    if any(term in name for term in REPRINT):
        return "ignore", "reprint/restock"
    if not status_text or not status_text.strip():
        return "unknown", "missing product-level status"
    if any(term in status_text for term in NEGATIVE):
        return "not_available", "preorder, sold out or unavailable"
    if release_date:
        try:
            day = date.fromisoformat(release_date)
        except ValueError:
            return "unknown", "invalid release date"
        if day > today:
            return "not_available", "future release date"
    else:
        return "unknown", "release date not verified"
    if any(term in status_text for term in POSITIVE):
        return "candidate_in_stock", "stock signal; independent new-release review required"
    return "unknown", "no affirmative stock signal"
