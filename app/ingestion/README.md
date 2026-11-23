# ingestion

## But
Préparer l’import local de factures depuis différents formats.

## Contenu
| Fichier | Rôle |
|---|---|
| excel.py | Import CSV et XLSX avec mappage de colonnes configurable |
| ubl.py | Lecture d'une facture UBL avec analyse XML sans réseau |
| pdf_text.py | Extraction PDF prévue |
| ocr.py | OCR optionnel prévu |
| champs.py | Modèles Pydantic pour factures, paiements et flux |

## Entrées / Sorties
CSV/XLSX locaux (factures, paiements et flux) ou UBL vers modèles Pydantic ; les cellules numériques sont lues comme texte puis converties en `Decimal`. Le mappage de colonnes est configurable.

## Règles et décisions
Les ICE doivent avoir 15 chiffres, les montants sont validés et HT + TVA doit égaler TTC. Toute facture lue depuis un document devra passer par une validation humaine avant calcul. CSV et XLSX sont couverts ; `.xls` n'est pas pris en charge. 2026-11-23.

## Comment tester
`pytest -q tests/test_extraction.py`

## État d’avancement
- [x] Import CSV/XLSX/UBL et validation — 2026-11-23

## Limites connues et prochaines étapes
L'extraction PDF/OCR et l'écran de validation restent prévus en phases 5 et 6.
