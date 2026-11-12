
# equipe.py - Systeme de duel
def duel(nom_A, info_A, nom_B, info_B):
    score_A = 0
    score_B = 0
    score_A += info_A.get("forme", 0) * 2
    score_B += info_B.get("forme", 0) * 2
    score_A += info_A.get("motivation", 5)
    score_B += info_B.get("motivation", 5)
    if info_A.get("buteur_present"):
        score_A += 3
    if info_B.get("buteur_present"):
        score_B += 3
    if info_A.get("gardien_present"):
        score_A += 2
    if info_B.get("gardien_present"):
        score_B += 2
    if info_A.get("jours_repos", 4) >= 4:
        score_A += 1
    if info_B.get("jours_repos", 4) >= 4:
        score_B += 1
    if info_A.get("mt_fin_favorable"):
        score_A += 2
    if info_B.get("mt_fin_favorable"):
        score_B += 2
    ecart = abs(score_A - score_B)
    if score_A > score_B:
        verdict = f"{nom_A} favori"
    elif score_B > score_A:
        verdict = f"{nom_B} favori"
    else:
        verdict = "Equilibre"
    return {"A": {"score": score_A}, "B": {"score": score_B}, "ecart": ecart, "verdict": verdict}


