# securite.py - Protection du bot
import os
import hashlib
from datetime import datetime

def verifier_secrets():
    manquants = []
    if not os.getenv("TELEGRAM_TOKEN"):
        manquants.append("TELEGRAM_TOKEN")
    if not os.getenv("TELEGRAM_CHAT_ID"):
        manquants.append("TELEGRAM_CHAT_ID")
    if not os.getenv("API_FOOTBALL_KEY"):
        manquants.append("API_FOOTBALL_KEY")
    if manquants:
        return False, manquants
    return True, []

def verifier_coupon_securite(coupon):
    if not coupon:
        return False, "Aucun match favori trouvé (ecart < 2). Pas de coupon."
    if len(coupon) > 5:
        return False, "Trop de matchs, on limite à 5."
    return True, "OK"

def _hash_texte(texte):
    return hashlib.md5(texte.encode()).hexdigest()

def deja_envoye_aujourd_hui(texte_coupon):
    try:
        if not os.path.exists("dernier_coupon.txt"):
            return False
        with open("dernier_coupon.txt", "r", encoding="utf-8") as f:
            contenu = f.read()
        today = datetime.now().strftime("%Y-%m-%d")
        h = _hash_texte(texte_coupon)
        return today in contenu and h in contenu
    except Exception:
        return False

def sauvegarder_coupon(texte_coupon):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        h = _hash_texte(texte_coupon)
        with open("dernier_coupon.txt", "w", encoding="utf-8") as f:
            f.write(f"{today}\n{h}")
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")


