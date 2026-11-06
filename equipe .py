python
# systemes/equipe.py - VERSION FINALE NETTOYEE
# L'ANALYSTE - Il fait uniquement le duel, il ne fait pas de coupon
# Il reçoit les infos déjà remplies par main.py via les vraies API
# AUCUNE FONCTION EN DOUBLE

def comprendre_equipe(nom, info):
    """
    Teste une équipe sur 6 cases.
    info vient de main.py -> construire_info_equipe_auto()
    qui a déjà rempli forme, buteur, gardien, motivation, repos, mt_fin
    avec les vraies API TheSportsDB + API-Football.
    """
    score = 0
    cases = {}

    # 1. Forme : 3 victoires ou plus sur les 5 derniers
    if info.get("forme", 0) >= 3:
        cases["forme"] = True
        score += 1
    else:
        cases["forme"] = False

    # 2. Buteur présent : vient de API-Football / injuries
    if info.get("buteur_present", False):
        cases["buteur"] = True
        score += 1
    else:
        cases["buteur"] = False

    # 3. Gardien présent : vient de API-Football / injuries
    if info.get("gardien_present", False):
        cases["gardien"] = True
        score += 1
    else:
        cases["gardien"] = False

    # 4. Motivation : 7/10 ou plus
    if info.get("motivation", 0) >= 7:
        cases["motivation"] = True
        score += 1
    else:
        cases["motivation"] = False

    # 5. Repos : 3 jours ou plus, calculé avec TheSportsDB
    # date_prochain - date_dernier
    if info.get("jours_repos", 0) >= 3:
        cases["repos"] = True
        score += 1
    else:
        cases["repos"] = False

    # 6. MT / Fin favorable : gagne souvent en 2e mi-temps
    if info.get("mt_fin_favorable", False):
        cases["mt_fin"] = True
        score += 1
    else:
        cases["mt_fin"] = False

    return {"nom": nom, "score": score, "cases": cases}


def duel(equipe_A, info_A, equipe_B, info_B):
    """
    Compare les 2 équipes opposées avant de donner un résultat.
    C'est cette fonction que main.py appelle dans detecter_matchs_semaine_auto()
    """
    res_A = comprendre_equipe(equipe_A, info_A)
    res_B = comprendre_equipe(equipe_B, info_B)
    ecart = res_A["score"] - res_B["score"]

    if ecart >= 3:
        verdict = "GROS FAVORI"
    elif ecart == 2:
        verdict = "FAVORI"
    elif ecart == 1:
        verdict = "MATCH SERRE"
    elif ecart == 0:
        verdict = "EGALITE - NE JOUE PAS"
    else:
        verdict = "SURPRISE POSSIBLE"

    return {"A": res_A, "B": res_B, "ecart": ecart, "verdict": verdict}

