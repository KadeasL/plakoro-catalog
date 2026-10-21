import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from translate import localize_title, enrich_candidate

class LocalizationTests(unittest.TestCase):
    def test_known_japanese_term(self):
        result = localize_title("プラコロ アドベンチャーボックス")
        self.assertEqual(result["name_ru"], "Плакоро Приключенческий набор")
        self.assertEqual(result["translation_status"], "draft_needs_review")

    def test_unknown_japanese_stays_untranslated(self):
        result = localize_title("プラコロ 未確認商品")
        self.assertIsNone(result["name_ru"])
        self.assertEqual(result["translation_status"], "needs_review")

    def test_unknown_english_stays_untranslated(self):
        self.assertIsNone(localize_title("Mystery New Product")["name_ru"])

    def test_candidate_keeps_original(self):
        item = enrich_candidate({"title": "プラコロ", "url": "https://example.org/item"})
        self.assertEqual(item["name_ja"], "プラコロ")
        self.assertEqual(item["name_ru"], "Плакоро")
        self.assertEqual(item["url"], "https://example.org/item")

if __name__ == "__main__":
    unittest.main()
