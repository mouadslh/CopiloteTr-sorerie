# demo

## But
Contenir les fichiers fictifs produits pour le scénario Menuiserie Atlas.

## Contenu
| Fichier | Rôle |
|---|---|
| factures.csv | 15 factures historiques payées et 3 factures Atlas impayées |
| paiements.csv | 15 paiements historiques associés |
| flux_prevus.csv | Deux décaissements de novembre 2026 |
| factures_bruitees.csv | Deux cas de validation invalides, hors jeu principal |
| exemple_ubl.xml | Exemple UBL fictif |

## Entrées / Sorties
CSV/XML générés localement par `python data/generer_demo.py` ; contenu principal : 35 lignes hors en-têtes.

## Règles et décisions
Toutes les données sont fictives. 2026-11-23.

## Comment tester
`python data/generer_demo.py`

## État d’avancement
- [x] Jeu fictif généré et vérifié — 2026-11-23

## Limites connues et prochaines étapes
Les valeurs ne représentent aucun client réel ; les deux lignes bruitées doivent être rejetées par la validation.
