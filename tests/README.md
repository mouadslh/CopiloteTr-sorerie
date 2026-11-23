# tests

## But
Vérifier les règles et comportements du Copilote.

## Contenu
| Fichier | Rôle |
|---|---|
| test_moteur.py | Tests du moteur légal |
| test_simulation.py | Tests de simulation prévus |
| test_extraction.py | Tests Pydantic et imports CSV/XLSX/UBL |
| test_phase2.py | Tests du dépôt SQLite, des profils et des données Atlas |
| test_atlas.py | Tests d'acceptation des échéances et amendes Atlas |

## Entrées / Sorties
Données de test fictives ; résultats pytest.

## Règles et décisions
Montants calculés en Decimal. 2026-11-23.

## Comment tester
`pytest -q`

## État d’avancement
- [x] Tests des phases 1 et 2 — 27 tests réussis le 2026-11-23

## Limites connues et prochaines étapes
Simulation, actions et interface seront testées dans les phases suivantes.
