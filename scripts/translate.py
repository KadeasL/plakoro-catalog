"""Conservative Russian localization for Plakoro candidate titles.

Unknown text is NEVER machine-translated or published automatically.
"""
import re

POKEMON = {
    "pinsir": "Пинсир", "カイロス": "Пинсир",
    "moltres": "Молтрес", "ファイヤー": "Молтрес",
    "articuno": "Артикуно", "フリーザー": "Артикуно",
    "zapdos": "Запдос", "サンダー": "Запдос",
    "onix": "Оникс", "イワーク": "Оникс",
    "grimer": "Граймер", "ベトベター": "Граймер",
    "bulbasaur": "Бульбазавр", "フシギダネ": "Бульбазавр",
}
TERMS = {
    "アドベンチャーボックス": "Приключенческий набор",
    "スターターセット": "Стартовый набор",
    "プラコロ": "Плакоро",
}

def localize_title(title):
    """Return a proposed Russian title only when every token is recognized.

    Titles containing unrecognized Japanese characters remain untranslated.
    """
    if not isinstance(title, str) or not title.strip():
        return {"name_ru": None, "translation_status": "needs_review"}
    output = title.strip()
    for src, dest in sorted(TERMS.items(), key=lambda p: -len(p[0])):
        output = output.replace(src, dest)
    for src, dest in sorted(POKEMON.items(), key=lambda p: -len(p[0])):
        output = re.sub(re.escape(src), dest, output, flags=re.I)
    if re.search(r"[\u3040-\u30ff\u3400-\u9fff]", output):
        return {"name_ru": None, "translation_status": "needs_review"}
    if output == title.strip():
        return {"name_ru": None, "translation_status": "needs_review"}
    return {"name_ru": output, "translation_status": "draft_needs_review"}

def enrich_candidate(candidate):
    title = candidate.get("title", "")
    proposal = localize_title(title)
    return {**candidate, "name_ja": title if re.search(r"[\u3040-\u30ff\u3400-\u9fff]", title) else None,
            "name_en": title if title.isascii() else None, **proposal}
