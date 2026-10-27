#!/usr/bin/env python3
"""Email only independently reviewed Plakoro releases, never raw candidates."""
import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "catalog" / "confirmed_on_sale.json"
STATE = ROOT / "catalog" / "notified_sales.json"

def read(path, fallback):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else fallback

def valid(item):
    required = ("id", "name_ja", "name_ru", "price_jpy", "sale_date", "shop_url", "evidence_url")
    if not all(item.get(k) for k in required):
        return False
    if item.get("status") != "confirmed_on_sale" or item.get("available_now") is not True:
        return False
    return all(urlparse(item[k]).scheme == "https" and urlparse(item[k]).netloc
               for k in ("shop_url", "evidence_url"))

def main():
    sender = os.environ.get("GMAIL_SENDER", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")
    recipient = os.environ.get("PLAKORO_RECIPIENT", "")
    if not (sender and password and recipient):
        print("Mail credentials/recipient not configured; no email sent.")
        return
    records = read(INPUT, {"releases": []})["releases"]
    sent = set(read(STATE, {"sent_ids": []})["sent_ids"])
    changed = False
    for item in records:
        if not valid(item) or item["id"] in sent:
            continue
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = "Plakoro: подтверждена продажа — " + item["name_ru"]
        msg.set_content(
            f"Новый набор Plakoro в продаже в Японии!\n\n"
            f"{item['name_ru']} / {item['name_ja']}\n"
            f"Цена: {item['price_jpy']} JPY\n"
            f"Дата начала продаж: {item['sale_date']}\n"
            f"Купить: {item['shop_url']}\n"
            f"Подтверждение: {item['evidence_url']}\n"
        )
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=30) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
        sent.add(item["id"])
        changed = True
        print("Sent:", item["id"])
    if changed:
        STATE.write_text(json.dumps({"sent_ids": sorted(sent)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
