# ingestion

## But
Préparer l’import local de factures depuis différents formats.

## Contenu
| Fichier | Rôle |
|---|---|
| excel.py | Import tabulaire prévu |
| ubl.py | Lecture UBL prévue |
| pdf_text.py | Extraction PDF prévue |
| ocr.py | OCR optionnel prévu |
| champs.py | Extraction et validation des champs prévue |

## Entrées / Sorties
Fichiers locaux vers données structurées.

## Règles et décisions
Toute extraction nécessitera une validation humaine avant calcul. 2026-11-23.

## Comment tester
`pytest -q tests/test_extraction.py`

## État d’avancement
- [x] README de squelette créé — 2026-11-23

## Limites connues et prochaines étapes
Fonctionnalités prévues en phases ultérieures.
