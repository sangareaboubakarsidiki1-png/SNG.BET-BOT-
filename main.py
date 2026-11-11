

python
# main.py - SNG BET BOT - VERSION COUPON REEL
# Le CHEF : il appelle equipe.py, récupère les matchs, construit le coupon

import os
import requests
from datetime import datetime, timedelta
from equipe import duel

# --- 1. CLES DEPUIS GITHUB SECRETS ---
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

# --- 2. CONSTRUIRE INFO EQUIPE AVEC LES VRAIES API ---
def construire_info_equipe_auto(nom_equipe, team_id_api=None):
    """
    Remplit les 6 cases avec les vraies API.
    Si une API ne répond pas, on met une valeur neutre pour ne pas planter.
    """
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
        # A. Forme : 5 derniers matchs
        url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id_api}&season=2024&league=39"
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json().get("response", {})
            form = data.get("form", "")  # Ex: "WWDLW"
            if form:
                info["forme"] = form.count("W")

        # B. Blessés : buteur / gardien absents ?
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

        # C. Motivation simple : si forme >= 3, motivation haute
        if info["forme"] >= 3:
            info["motivation"] = 8
        elif info["forme"] == 2:
            info["motivation"] = 7
        else:
            info["motivation"] = 5

    except Exception as e:
        print(f"Erreur API pour {nom_equipe}: {e}")

    return info

# --- 3. DETECTER MATCHS + FAIRE DUELS + CONSTRUIRE COUPON ---
def detecter_matchs_semaine_auto():
    if not API_FOOTBALL_KEY:
        envoyer_telegram("⚠️ <b>SNG BET BOT</b>\nClé API-Football manquante dans Secrets. Ajoute API_FOOTBALL_KEY.")
        return

    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    # On prend les grosses ligues : Angleterre, Espagne, France, Italie, Allemagne
    ligues = [39, 140, 61, 135, 78]
    coupon = []
    analyses = []

    for league in ligues:
        try:
            # Matchs des 7 prochains jours
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

        for m in matchs[:10]:  # Max 10 par ligue pour ne pas saturer
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

    # --- 4. ENVOYER LE COUPON ---
    if not coupon:
        envoyer_telegram("📊 <b>SNG BET BOT - Analyse semaine</b>\n\nAucun GROS FAVORI trouvé cette semaine.\nOn ne joue pas pour ne pas perdre. ❌\n\nRègle: on joue seulement si écart >= 2.")
    else:
        # On limite à 3 matchs pour un combiné raisonnable
        selection = coupon[:3]
        texte = "🔥 <b>SNG BET BOT - COUPON REEL DE LA SEMAINE</b> 🔥\n\n"
        texte += "\n".join(selection)
        texte += "\n\n📋 <b>Analyses :</b>\n" + "\n".join(analyses[:3])
        texte += "\n⚠️ Joue responsable. Mise conseillée: 1-2% de ton budget."
        envoyer_telegram(texte)

    print("Termine.")

if __name__ == "__main__":
    detecter_matchs_semaine_auto()


