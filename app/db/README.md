# db

## But
Gérer le stockage SQLite local.

## Contenu
| Fichier | Rôle |
|---|---|
| schema.sql | Tables SQLite de l'application |
| depot.py | Dépôt SQLite avec requêtes paramétrées et audit |

## Entrées / Sorties
Modèles validés vers une base SQLite locale ; montants stockés en texte décimal pour préserver leur précision.

## Règles et décisions
SQLite via bibliothèque standard. Les créations/modifications de factures et de paramètres légaux sont journalisées dans `audit`. 2026-11-23.

## Comment tester
`pytest -q`

## État d’avancement
- [x] Schéma et dépôt SQLite implémentés — 2026-11-23

## Limites connues et prochaines étapes
Pas encore de migration de schéma ; le prototype utilise `CREATE TABLE IF NOT EXISTS`.
