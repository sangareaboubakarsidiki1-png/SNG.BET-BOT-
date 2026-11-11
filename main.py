python
import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("Demarrage du bot...")

if not TOKEN or not CHAT_ID:
    print("ERREUR: TOKEN ou CHAT_ID manquant dans Secrets")
else:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": "✅ SNG BET BOT est en ligne ! Le test marche."}
    r = requests.post(url, data=data)
    print("Telegram reponse:", r.status_code)
    print(r.text)

print("Termine.")

