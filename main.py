

python
# main.py - VERSION FINALE NETTOYEE - LIT LES VRAIES API
# 10 bases + Duel equipe.py + MT/Fin + Detection Auto + Alerte + Scheduler
# AUCUNE FONCTION EN DOUBLE - AUCUNE FONCTION DE TEST
import os
import time
import threading
import datetime
import requests
from systemes.equipe import duel

# --- SECRETS GITHUB ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
API_KEY_1 = os.environ.get("API_KEY_1", "")  # TheSportsDB
API_KEY_2 = os.environ.get("API_KEY_2", "")  # API-Football

# --- 10 BASES ---
NOMS_BASE = {
    "PSG": "Paris Saint-Germain",
    "Real Madrid": "Real Madrid",
    "Man City": "Manchester City",
    "Inter Milan": "Inter",
    "Wydad": "Wydad Casablanca",
    "ASEC": "ASEC Mimosas",
    "Flamengo": "Flamengo",
    "Al Ahly": "Al Ahly",
    "Inter Miami": "Inter Miami",
    "Stade Abidjan": "Stade d'Abidjan",
}

EQUIPES_ORIGINE = {
    "PSG": ("Ligue 1 France", 88),
    "Real Madrid": ("La Liga", 90),
    "Man City": ("Premier League", 89),
    "Inter Milan": ("Serie A", 86),
    "Wydad": ("Botola Maroc", 72),
    "ASEC": ("Ligue 1 Cote d'Ivoire", 68),
    "Flamengo": ("Brasileirao", 82),
    "Al Ahly": ("Premier League Egypte", 76),
    "Inter Miami": ("MLS", 74),
    "Stade Abidjan": ("Ligue 1 Cote d'Ivoire", 65),
}

LIGUES_COEF = {
    "Ligue 1 France": 1.0, "La Liga": 1.0, "Premier League": 1.0,
    "Serie A": 1.0, "Botola Maroc": 0.45, "Ligue 1 Cote d'Ivoire": 0.35,
    "Brasileirao": 0.85, "Premier League Egypte": 0.5, "MLS": 0.65,
}

# --- API REELLE : TheSportsDB ---
def get_id_equipe_thesportsdb(nom_equipe):
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY_1}/searchteams.php"
        r = requests.get(url, params={"t": nom_equipe}, timeout=15)
        data = r.json()
        teams = data.get("teams", [])
        if teams:
            return teams[0].get("idTeam")
    except Exception as e:
        print(f"Erreur searchteams {nom_equipe} : {e}")
    return None

def get_prochains_matchs_api1(nom_equipe):
    # VRAIE API : prochain match
    try:
        team_id = get_id_equipe_thesportsdb(nom_equipe)
        if not team_id:
            return []
        url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY_1}/eventsnext.php"
        r = requests.get(url, params={"id": team_id}, timeout=15)
        data = r.json()
        events = data.get("events", []) or []
        result = []
        for ev in events[:1]:
            result.append({
                "dateEvent": ev.get("dateEvent"),
                "strTime": ev.get("strTime"),
                "strHomeTeam": ev.get("strHomeTeam"),
                "strAwayTeam": ev.get("strAwayTeam"),
                "idEvent": ev.get("idEvent"),
            })
        return result
    except Exception as e:
        print(f"Erreur eventsnext {nom_equipe} : {e}")
        return []

def get_5_derniers_api2(nom_equipe):
    # VRAIE API : 5 derniers résultats V / N / D
    try:
        team_id = get_id_equipe_thesportsdb(nom_equipe)
        if not team_id:
            return ["N", "N", "N", "N", "N"]
        url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY_1}/eventslast.php"
        r = requests.get(url, params={"id": team_id}, timeout=15)
        data = r.json()
        events = data.get("results", []) or []
        resultats = []
        for ev in events[:5]:
            home = ev.get("strHomeTeam")
            score_home = ev.get("intHomeScore")
            score_away = ev.get("intAwayScore")
            if score_home is None or score_away is None:
                continue
            score_home = int(score_home)
            score_away = int(score_away)
            is_home = (nom_equipe in str(home)) or (home == nom_equipe)
            if is_home:
                if score_home > score_away:
                    resultats.append("V")
                elif score_home == score_away:
                    resultats.append("N")
                else:
                    resultats.append("D")
            else:
                if score_away > score_home:
                    resultats.append("V")
                elif score_away == score_home:
                    resultats.append("N")
                else:
                    resultats.append("D")
        while len(resultats) < 5:
            resultats.append("N")
        return resultats[:5]
    except Exception as e:
        print(f"Erreur eventslast {nom_equipe} : {e}")
        return ["N", "N", "N", "N", "N"]

def get_date_dernier_match(nom_equipe):
    # Pour calculer les jours de repos
    try:
        team_id = get_id_equipe_thesportsdb(nom_equipe)
        if not team_id:
            return None
        url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY_1}/eventslast.php"
        r = requests.get(url, params={"id": team_id}, timeout=15)
        data = r.json()
        events = data.get("results", []) or []
        if events:
            return events[0].get("dateEvent")
    except Exception as e:
        print(f"Erreur date dernier {nom_equipe} : {e}")
    return None

def calculer_jours_repos(date_dernier, date_prochain):
    try:
        if not date_dernier or not date_prochain:
            return 5
        d1 = datetime.datetime.strptime(date_dernier, "%Y-%m-%d").date()
        d2 = datetime.datetime.strptime(date_prochain, "%Y-%m-%d").date()
        return (d2 - d1).days
    except:
        return 5

# --- API REELLE : API-Football pour les blessés ---
def get_blesses_api_football(nom_equipe):
    try:
        if not API_KEY_2:
            return {"buteur_present": True, "gardien_present": True, "source": "Pas de cle API-Football, on suppose presents"}
        headers = {"x-rapidapi-key": API_KEY_2, "x-rapidapi-host": "v3.football.api-sports.io"}
        r = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params={"name": nom_equipe}, timeout=15)
        teams = r.json().get("response", [])
        if not teams:
            return {"buteur_present": True, "gardien_present": True, "source": "Equipe non trouvee API-Football"}
        team_id = teams[0]["team"]["id"]
        r2 = requests.get("https://v3.football.api-sports.io/injuries", headers=headers, params={"team": team_id, "season": 2026}, timeout=15)
        injuries = r2.json().get("response", [])
        buteur_absent = any("Forward" in str(i.get("player", {}).get("position", "")) for i in injuries)
        gardien_absent = any("Goalkeeper" in str(i.get("player", {}).get("position", "")) for i in injuries)
        return {
            "buteur_present": not buteur_absent,
            "gardien_present": not gardien_absent,
            "source": f"{len(injuries)} blesses trouves API-Football"
        }
    except Exception as e:
        print(f"Erreur injuries {nom_equipe} : {e}")
        return {"buteur_present": True, "gardien_present": True, "source": "Erreur API, on suppose presents"}

# --- CALCULS ---
def estimer_force_x(resultats):
    pts = sum([3 if r == "V" else 1 if r == "N" else 0 for r in resultats])
    return 55 + pts * 2

def fusionner_resultats(nom, id_base):
    res = get_5_derniers_api2(nom)
    return res, 0.8, "Fusion OK"

def calcul_score_final(force, resultats, coef):
    pts = sum([3 if r == "V" else 1 if r == "N" else 0 for r in resultats])
    score = force * 0.6 + pts * 2 * coef + 10
    return round(min(score, 95), 1), "Score calcule"

def calculer_proba_match(score_a, score_b):
    diff = score_a - score_b
    if diff > 20:
        return {"V1": 68, "X": 20, "V2": 12}
    elif diff > 10:
        return {"V1": 58, "X": 24, "V2": 18}
    elif diff < -20:
        return {"V1": 12, "X": 20, "V2": 68}
    elif diff < -10:
        return {"V1": 18, "X": 24, "V2": 58}
    else:
        return {"V1": 32, "X": 36, "V2": 32}

def check_prevention(nom_a, score_a, nom_b, score_b):
    ecart = abs(score_a - score_b)
    if ecart < 5:
        return False, ecart, 0, "⚠️ Ecart trop petit, match trop serre. PREVENTION : NE JOUE PAS"
    return True, ecart, max(score_a, score_b), "OK"

# --- DUEL + MT / FIN ---
def construire_info_equipe_auto(nom_equipe, score_final, resultats, date_prochain):
    date_dernier = get_date_dernier_match(nom_equipe)
    jours_repos = calculer_jours_repos(date_dernier, date_prochain)
    blesses = get_blesses_api_football(nom_equipe)
    forme = sum([1 for r in resultats if r == "V"])
    mt_fin = True if forme >= 3 else False
    return {
        "forme": forme,
        "buteur_present": blesses["buteur_present"],
        "gardien_present": blesses["gardien_present"],
        "motivation": 8 if score_final > 70 else 6,
        "jours_repos": jours_repos,
        "mt_fin_favorable": mt_fin,
    }

def proposer_mt_fin(resultat_duel):
    ecart = resultat_duel["ecart"]
    A = resultat_duel["A"]
    B = resultat_duel["B"]
    coupons = []
    if ecart >= 2:
        coupons.append(("SAFE", "X/V1 (N/1)", f"{B['nom']} defend en 1ere, {A['nom']} pousse en 2e"))
        coupons.append(("MOYEN", "V1/V1 (1/1)", f"Si {A['nom']} marque vite"))
        coupons.append(("A EVITER", "V2/V1 (2/1)", f"{B['nom']} mene rarement a la mi-temps"))
    elif ecart == 1:
        coupons.append(("SAFE", "X/X (N/N)", "Match serre, nul probable"))
        coupons.append(("MOYEN", "X/V1 (N/1)", "Le favori se reveille en 2e"))
    elif ecart == 0:
        coupons.append(("NE JOUE PAS", "AUCUN", "Trop egal, trop risque"))
    else:
        coupons.append(("SURPRISE", "X/V2 (N/2)", "L'outsider est plus en forme"))
        coupons.append(("MOYEN", "V2/V2 (2/2)", "Si l'outsider confirme"))
    return coupons

def formater_coupons_avec_triples(nom_a, nom_b, groupe, ecart):
    txt = f"Double : {nom_a} ou N\n"
    txt += f"Triple : {nom_a} / N / {nom_b} avec prevention\n"
    txt += f"Groupe {groupe} - Ecart {ecart:.1f}%\n"
    return txt

# --- DETECTION AUTO ---
def detecter_matchs_semaine_auto():
    matchs_trouves = []
    matchs_non_trouves = []
    for nom_base, id_base in NOMS_BASE.items():
        ligue_base, force_base = EQUIPES_ORIGINE[nom_base]
        coef_base = LIGUES_COEF.get(ligue_base, 0.5)
        res_base, _, _ = fusionner_resultats(id_base, nom_base)
        score_base, _ = calcul_score_final(force_base, res_base, coef_base)

        events = get_prochains_matchs_api1(id_base)
        if not events:
            matchs_non_trouves.append(nom_base)
            continue

        ev = events[0]
        domicile = ev.get("strHomeTeam", "")
        exterieur = ev.get("strAwayTeam", "")
        date_prochain = ev.get("dateEvent", "")
        # Qui est l'adversaire ?
        if domicile == id_base or id_base in str(domicile):
            adversaire = exterieur
        else:
            adversaire = domicile

        res_adv = get_5_derniers_api2(adversaire)
        force_adv = estimer_force_x(res_adv)
        score_adv, _ = calcul_score_final(force_adv, res_adv, 0.35)

        info_A = construire_info_equipe_auto(nom_base, score_base, res_base, date_prochain)
        info_B = construire_info_equipe_auto(adversaire, score_adv, res_adv, date_prochain)

        if domicile == id_base or id_base in str(domicile):
            resultat_duel = duel(nom_base, info_A, adversaire, info_B)
            score_a, score_b = score_base, score_adv
            nom_a, nom_b = nom_base, adversaire
        else:
            resultat_duel = duel(adversaire, info_B, nom_base, info_A)
            score_a, score_b = score_adv, score_base
            nom_a, nom_b = adversaire, nom_base

        probas = calculer_proba_match(score_a, score_b)
        autorise, ecart, _, msg_prevention = check_prevention(nom_a, score_a, nom_b, score_b)
        groupe = "TOP" if score_base > 50 else "FLOP"

        matchs_trouves.append({
            "nom_base": nom_base, "ligue": ligue_base, "adversaire": adversaire,
            "date": date_prochain, "heure": ev.get("strTime"),
            "domicile": domicile, "exterieur": exterieur,
            "nom_a": nom_a, "nom_b": nom_b, "score_a": score_a, "score_b": score_b,
            "probas": probas, "ecart": ecart, "groupe": groupe,
            "autorise": autorise, "msg_prevention": msg_prevention,
            "duel": resultat_duel,
        })
    return matchs_trouves, matchs_non_trouves

# --- TELEGRAM ---
def envoyer_telegram(message, chat_id=None):
    cid = chat_id or TELEGRAM_CHAT_ID
    if not TELEGRAM_TOKEN or not cid:
        print(message)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for i in range(0, len(message), 4000):
        try:
            requests.post(url, data={"chat_id": cid, "text": message[i:i+4000]}, timeout=15)
        except Exception as e:
            print("Erreur Telegram:", e)

def formater_alerte_semaine(matchs, non_trouves):
    today = datetime.date.today().strftime("%d %b %Y")
    texte = f"ALERTE SEMAINE - {today}\n\n"
    if not matchs:
        texte += "Aucune de tes 10 bases ne joue cette semaine.\n"
        return texte
    texte += f"Cette semaine, {len(matchs)} de tes bases jouent :\n\n"
    for i, m in enumerate(matchs, 1):
        texte += f"--- MATCH {i} ---\n"
        texte += f"{m['domicile']} vs {m['exterieur']}\n"
        texte += f"Date : {m['date']} a {m['heure']}\n"
        texte += f"Ligue : {m['ligue']}\n"
        texte += f"DUEL equipe.py : {m['duel']['A']['nom']} {m['duel']['A']['score']}/6 vs {m['duel']['B']['nom']} {m['duel']['B']['score']}/6\n"
        texte += f"Ecart duel : {m['duel']['ecart']} => {m['duel']['verdict']}\n"
        texte += f"Score estime : {m['nom_a']} {m['score_a']} vs {m['nom_b']} {m['score_b']}\n"
        texte += f"Proba : V1 {m['probas']['V1']}% / X {m['probas']['X']}% / V2 {m['probas']['V2']}%\n"
        if not m['autorise']:
            texte += f"\n{m['msg_prevention']}\nBLOQUE, on ne fait pas de coupons.\n"
        else:
            texte += f"\nCoupons Doubles + Triples :\n"
            texte += formater_coupons_avec_triples(m['nom_a'], m['nom_b'], m['groupe'], m['ecart'])
            texte += f"\n🎟️ COUPONS MT / FIN (ton jeu) :\n"
            for type_c, coupon, pourquoi in proposer_mt_fin(m['duel']):
                texte += f"{type_c} : {coupon} - {pourquoi}\n"
        texte += f"\n====================\n\n"
    if non_trouves:
        texte += f"Autres bases sans match : {', '.join(non_trouves)}\n"
    texte += "\n👉 A TOI DE VALIDER. Le bot propose, toi tu decides."
    return texte

def envoyer_alerte_semaine_auto(chat_id):
    try:
        matchs, non_trouves = detecter_matchs_semaine_auto()
        texte = formater_alerte_semaine(matchs, non_trouves)
        envoyer_telegram(texte, chat_id)
        print(f"Alerte envoyee : {len(matchs)} matchs")
    except Exception as e:
        print(f"Erreur alerte : {e}")

# --- SCHEDULER ---
def scheduler_hebdo(chat_id):
    deja_envoye = None
    while True:
        try:
            now = datetime.datetime.now()
            if now.weekday() == 0 and now.hour == 8 and deja_envoye != now.date():
                print("Scheduler : Lundi 08h00, j'envoie alerte")
                envoyer_alerte_semaine_auto(chat_id)
                deja_envoye = now.date()
            time.sleep(300)
        except Exception as e:
            print(f"Erreur scheduler : {e}")
            time.sleep(300)

def demarrer_scheduler(chat_id):
    t = threading.Thread(target=scheduler_hebdo, args=(chat_id,), daemon=True)
    t.start()

# --- LANCEMENT ---
if __name__ == "__main__":
    print("Lancement bot - version nettoyee API reelle...")
    envoyer_alerte_semaine_auto(TELEGRAM_CHAT_ID)


