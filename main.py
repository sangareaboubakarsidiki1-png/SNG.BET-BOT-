

python
# main.py - SNG BET BOT - VERSION COUPON REEL + SECURITE
# Le CHEF : il utilise equipe.py pour le duel + securite.py pour protéger

import os
import requests
from datetime import datetime, timedelta
from equipe import duel
from securite import verifier_secrets, deja_envoye_aujourd_hui, sauvegarder_coupon, verifier_coupon_securite

# --- CLES DEPUIS GITHUB SECRETS ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

print("Demarrage du bot...")

def envoyer_telegram(texte):
    if not TOKEN or not CHAT_ID:
        print("ERREUR: TOKEN ou CHAT_ID manquant")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": texte, "parse_mode": "HTML"}
    r = requests.post(url, data=data)
    print("Telegram reponse:", r.status_code)

# --- CONSTRUIRE INFO EQUIPE AVEC LES VRAIES API ---
def construire_info_equipe_auto(nom_equipe, team_id_api=None):
    info = {
        "forme": 0,
        "buteur_present": True,
        "gardien_present": True,
        "motivation": 5,
        "jours_repos": 4,
        "mt_fin_favorable": False
    }

    if not API_FOOTBALL_KEY or not team_id_api:
        return info

    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    try:
        url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id_api}&season=2024&league=39"
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json().get("response", {})
            form = data.get("form", "")
            if form:
                info["forme"] = form.count("W")

        url2 = f"https://v3.football.api-sports.io/injuries?team={team_id_api}&season=2024"
        r2 = requests.get(url2, headers=headers, timeout=10)
        if r2.status_code == 200:
            blesses = r2.json().get("response", [])
            for b in blesses:
                pos = b.get("player", {}).get("position", "").lower()
                if "attack" in pos or "forward" in pos:
                    info["buteur_present"] = False
                if "goalkeeper" in pos:
                    info["gardien_present"] = False

        if info["forme"] >= 3:
            info["motivation"] = 8
        elif info["forme"] == 2:
            info["motivation"] = 7
        else:
            info["motivation"] = 5

    except Exception as e:
        print(f"Erreur API pour {nom_equipe}: {e}")

    return info

# --- DETECTER MATCHS + FAIRE DUELS + CONSTRUIRE COUPON ---
def detecter_matchs_semaine_auto():
    # 3. VERIFICATION AVANT LANCEMENT - Utilise securite.py
    ok, manquants = verifier_secrets()
    if not ok:
        envoyer_telegram(f"❌ <b>SNG BET BOT bloqué</b>\nIl manque : {', '.join(manquants)}\nVa dans Settings > Secrets > Actions")
        return

    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    ligues = [39, 140, 61, 135, 78]  # Angleterre, Espagne, France, Italie, Allemagne
    coupon = []
    analyses = []

    for league in ligues:
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            url = f"https://v3.football.api-sports.io/fixtures?league={league}&season=2024&from={today}&to={next_week}"
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                continue
            matchs = r.json().get("response", [])
        except Exception as e:
            print(f"Erreur ligue {league}: {e}")
            continue

        for m in matchs[:10]:
            equipe_A = m["teams"]["home"]["name"]
            equipe_B = m["teams"]["away"]["name"]
            id_A = m["teams"]["home"]["id"]
            id_B = m["teams"]["away"]["id"]
            date_match = m["fixture"]["date"][:16].replace("T", " ")

            info_A = construire_info_equipe_auto(equipe_A, id_A)
            info_B = construire_info_equipe_auto(equipe_B, id_B)

            resultat = duel(equipe_A, info_A, equipe_B, info_B)
            ecart = resultat["ecart"]
            verdict = resultat["verdict"]

            # REGLE COUPON REEL : on ne garde que les FAVORIS
            if ecart >= 2:
                gagnant = equipe_A if ecart > 0 else equipe_B
                coupon.append(f"✅ {equipe_A} vs {equipe_B} -> Victoire {gagnant} ({verdict})")
                analyses.append(f"🏟️ <b>{equipe_A} vs {equipe_B}</b> - {date_match}\nScore duel: {resultat['A']['score']} - {resultat['B']['score']} | {verdict}\n👉 Choix coupon: <b>{gagnant} gagne</b>\n")

    # --- SECURITE AVANT ENVOI - Utilise securite.py ---
    ok_secu, raison = verifier_coupon_securite(coupon)
    if not ok_secu:
        print(f"🛑 Coupon bloqué par sécurité : {raison}")
        envoyer_telegram(f"📊 <b>SNG BET BOT - Analyse semaine</b>\n\n🛑 Coupon bloqué par sécurité : {raison}\n\nOn ne joue pas pour ne pas perdre.")
        return

    # Anti-doublon
    texte_coupon = "\n".join(coupon)
    if deja_envoye_aujourd_hui(texte_coupon):
        print("Déjà envoyé aujourd'hui, on arrête.")
        return

    # Si tout est OK, on sauvegarde et on envoie
    sauvegarder_coupon(texte_coupon)

    selection = coupon[:3]
    texte = "🔥 <b>SNG BET BOT - COUPON REEL DE LA SEMAINE</b> 🔥\n\n"
    texte += "\n".join(selection)
    texte += "\n\n📋 <b>Analyses :</b>\n" + "\n".join(analyses[:3])
    texte += "\n⚠️ Joue responsable. Mise conseillée: 1-2% de ton budget."
    envoyer_telegram(texte)

    print("Termine.")

if __name__ == "__main__":
    detecter_matchs_semaine_auto()


