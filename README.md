# SNG.BET-BOT
Bot pour  coupons favoris
# BOT ANALYSEUR - DUEL + MT / FIN

Bot Telegram qui analyse les 10 bases, fait le duel des 2 équipes,
et propose des coupons MT / Fin. Le bot propose, toi tu valides.

## Ton jeu
Uniquement MT / Fin : X/V1, V1/V1, V2/V1, X/X, X/V2, V2/V2

## Fichiers

- `main.py` : Le cerveau. API, calculs, coupons, Telegram, scheduler.
- `systemes/equipe.py` : L'analyste. Teste les 6 cases et fait le duel.
- `.github/workflows/main.yml` : L'horloge. Lance le bot lundi 08h00.
- `check_doublons.py` : Vérifie qu'aucune fonction ne se répète.

## Les 6 cases de equipe.py

1. Forme : 3 victoires ou plus sur 5 derniers
2. Buteur présent : via API-Football / injuries
3. Gardien présent : via API-Football / injuries
4. Motivation : 7/10 ou plus
5. Repos : 3 jours ou plus, calculé avec TheSportsDB
6. MT / Fin favorable : gagne souvent en 2e mi-temps

Score : 5/6 ou 6/6 = BON, 4/6 = MOYEN, 0 à 3/6 = NE JOUE PAS

## Les 10 bases

PSG, Real Madrid, Man City, Inter Milan, Wydad, ASEC Mimosas,
Flamengo, Al Ahly, Inter Miami, Stade d'Abidjan

## Comment ça marche

1. Lundi 08h00, le workflow lance `main.py`
2. `main.py` check les 10 bases via TheSportsDB
3. Pour chaque base qui joue, il récupère :
   - 5 derniers résultats
   - Date prochain match + date dernier match = jours de repos
   - Blessés buteur / gardien via API-Football
4. Il calcule score final + proba V1 / X / V2
5. Il envoie les infos à `equipe.py` pour faire le duel
   Ex : PSG 5/6 vs Troyes 3/6, écart +2, FAVORI
6. Il transforme le duel en coupons MT / Fin
7. Il envoie 1 message Telegram par match

## Les coupons MT / Fin

- Ecart >= 2 : SAFE X/V1, MOYEN V1/V1, A EVITER V2/V1
- Ecart = 1 : SAFE X/X, MOYEN X/V1
- Ecart = 0 : NE JOUE PAS
- Ecart négatif : SURPRISE X/V2, MOYEN V2/V2

Il garde aussi les anciens coupons :
- Double : Favori ou N
- Triple : Favori / N / Adversaire avec prévention

## Exemple de message Telegram


ALERTE SEMAINE - 09 Nov 2026
Paris Saint-Germain vs Troyes
Date : 2026-11-07 a 20:05
DUEL : PSG 5/6 vs Troyes 3/6, Ecart +2 => FAVORI
Proba : V1 68% / X 20% / V2 12%
🎟️ COUPONS MT / FIN :
SAFE : X/V1 (N/1)
MOYEN : V1/V1 (1/1)
A EVITER : V2/V1 (2/1)
A TOI DE VALIDER. Le bot propose, toi tu decides.


## Secrets GitHub

Dans Settings > Secrets > Actions, mettre :

- TELEGRAM_TOKEN
- TELEGRAM_CHAT_ID
- API_KEY_1 : clé TheSportsDB
- API_KEY_2 : clé API-Football

Ne jamais mettre les clés dans le code.

## Comment tester

1. Lancer `python check_doublons.py` -> doit afficher 0 doublon
2. Aller dans GitHub > Actions > Run workflow
3. Vérifier la réception du message sur Telegram

## Règle d'or

Le bot ne décide jamais à ta place.
Il analyse, il propose, toi tu valides.
Si écart < 5, prévention : NE JOUE PAS.


