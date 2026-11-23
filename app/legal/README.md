# legal

## But
Calculer les échéances, retards et amendes estimées selon les paramètres versionnés.

## Contenu
| Fichier | Rôle |
|---|---|
| moteur.py | Fonctions pures avec traces |
| parametres.yaml | Paramètres datés |
| secteurs.yaml | Exceptions sectorielles prévues |

## Entrées / Sorties
Dates, montants Decimal et paramètres locaux ; résultats avec traces d’application.

## Règles et décisions
Hypothèses du prompt master, à confirmer dans docs/A_VALIDER.md. 2026-11-23.

## Comment tester
`pytest -q tests/test_moteur.py tests/test_atlas.py`

## État d’avancement
- [x] Moteur légal initial implémenté — 2026-11-23

## Limites connues et prochaines étapes
Aucune validation juridique ; convention des mois entamés : ceil(jours/30).
