# data

## But
Décrire et générer les données fictives de démonstration.

## Contenu
| Fichier | Rôle |
|---|---|
| generer_demo.py | Générateur fictif reproductible (graine 69) |
| demo/factures.csv | 18 factures payées ou impayées |
| demo/paiements.csv | 15 paiements historiques |
| demo/flux_prevus.csv | 2 décaissements |
| demo/factures_bruitees.csv | 2 entrées de validation, non intégrées au jeu principal |
| demo/exemple_ubl.xml | Facture UBL fictive |

## Entrées / Sorties
Données générées localement ; 35 lignes dans les trois tables du jeu principal, moins de 40 lignes de données au total en incluant les enregistrements dérivés. Tout est fictif.

## Règles et décisions
Aucune donnée réelle ou personnelle. 2026-11-23.

## Comment tester
`python data/generer_demo.py`

## État d’avancement
- [x] Générateur et jeu Atlas reproductible créés — 2026-11-23

## Limites connues et prochaines étapes
Le fichier bruité HT/TVA et l'ICE invalide sont des cas de test, pas des factures à importer dans la base.
