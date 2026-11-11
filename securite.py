python
# securite.py - NOUVELLE FONCTIONNALITE : Anti-doublon + Anti-perte
# Ce fichier n'existe nulle part ailleurs, il protège ton bot.

import os
from datetime import datetime

FICHIER_HISTORIQUE = "coupons_envoyes.txt"

def verifier_secrets():
    """3. VERIFICATION AVANT LANCEMENT - Si une clé manque, on dit laquelle."""
    manquants = []
    if not os.getenv("TELEGRAM_TOKEN"):
        manquants.append("TELEGRAM_TOKEN")
    if not os.getenv("TELEGRAM_CHAT_ID"):
        manquants.append("TELEGRAM_CHAT_ID")
    if not os.getenv("API_FOOTBALL_KEY"):
        manquants.append("API_FOOTBALL_KEY")

    if manquants:
        print(f"❌ LANCEMENT BLOQUE - Il manque : {', '.join(manquants)}")
        print("Va dans Settings > Secrets > Actions pour les ajouter.")
        return False, manquants

    print("✅ Toutes les clés sont là, on peut lancer.")
    return True, []

def deja_envoye_aujourd_hui(coupon_texte):
    """1. ANTI-DOUBLON - Ne pas envoyer 2 fois le même coupon le même jour."""
    aujourd_hui = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(FICHIER_HISTORIQUE):
        return False

    with open(FICHIER_HISTORIQUE, "r", encoding="utf-8") as f:
        contenu = f.read()
        # Si on a déjà envoyé ce même coupon aujourd'hui, on bloque
        if aujourd_hui in contenu and coupon_texte[:30] in contenu:
            print("⚠️ Coupon déjà envoyé aujourd'hui, on ne renvoie pas.")
            return True
    return False

def sauvegarder_coupon(coupon_texte):
    """Sauvegarde le coupon pour ne pas le renvoyer."""
    aujourd_hui = datetime.now().strftime("%Y-%m-%d")
    with open(FICHIER_HISTORIQUE, "a", encoding="utf-8") as f:
        f.write(f"\n--- {aujourd_hui} ---\n{coupon_texte}\n")

def verifier_coupon_securite(liste_coupon, cotes=[]):
    """
    1. ANTI-PERTE - Règles pour un vrai coupon réel.
    Retourne (ok, raison)
    """
    # Règle 1 : Pas plus de 3 matchs
    if len(liste_coupon) > 3:
        return False, "Trop de matchs, on limite à 3 pour ne pas perdre."

    # Règle 2 : Pas de coupon vide
    if len(liste_coupon) == 0:
        return False, "Aucun favori, on ne joue pas."

    # Règle 3 : Pas de cote trop basse (si on a les cotes)
    for cote in cotes:
        if cote < 1.30:
            return False, f"Cote {cote} trop basse, pas rentable."

    return True, "Coupon OK, on peut envoyer."


