python
# equipe.py - VERSION FINALE NETTOYEE
# L'ANALYSTE - Il fait uniquement le duel, il ne fait pas de coupon
# Il reçoit les infos déjà remplies par main.py via les vraies API
# AUCUNE FONCTION EN DOUBLE

def comprendre_equipe(nom, info):
    """ Teste une équipe sur 6 cases. """
    score = 0
    cases = {}

    # 1. Forme : 3 victoires ou plus sur les 5 derniers
    if info.get("forme", 0) >= 3:
        cases["forme"] = True
        score += 1
    else:
        cases["forme"] = False

    # 2. Buteur présent
    if info.get("buteur_present", False):
        cases["buteur"] = True
        score += 1
    else:
        cases["buteur"] = False

    # 3. Gardien présent
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

    # 5. Repos : 3 jours ou plus - accepte les 2 noms
    jours = info.get("jours_repos", info.get("repos", 0))
    if jours >= 3:
        cases["repos"] = True
        score += 1
    else:
        cases["repos"] = False

    # 6. MT / Fin favorable - accepte les 2 noms
    mt_fin = info.get("mt_fin_favorable", info.get("mt_fin", False))
    if mt_fin:
        cases["mt_fin"] = True
        score += 1
    else:
        cases["mt_fin"] = False

    return {"nom": nom, "score": score, "cases": cases}

def duel(equipe_A, info_A, equipe_B, info_B):
    """ Compare les 2 équipes opposées avant de donner un résultat. """
    res_A = comprendre_equipe(equipe_A, info_A)
    res_B = comprendre_equipe(equipe_B, info_B)
    ecart = res_A["score"] - res_B["score"]

    if ecart >= 3:
        verdict = "GROS FAVORI A"
    elif ecart == 2:
        verdict = "FAVORI A"
    elif ecart == 1:
        verdict = "MATCH SERRE - A"
    elif ecart == 0:
        verdict = "EGALITE - NE JOUE PAS"
    elif ecart == -1:
        verdict = "MATCH SERRE - B"
    elif ecart == -2:
        verdict = "FAVORI B"
    else:
        verdict = "GROS FAVORI B"

    return {"A": res_A, "B": res_B, "ecart": ecart, "verdict": verdict}


