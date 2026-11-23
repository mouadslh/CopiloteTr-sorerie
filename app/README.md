# app

## But
Regrouper les modules applicatifs du Copilote de trésorerie.

## Contenu
| Fichier | Rôle |
|---|---|
| legal/ | Calculs légaux déterministes |
| ingestion/ | Import des documents |
| payeurs/ | Profils payeurs |
| simulation/ | Prévisions de trésorerie |
| actions/ | Actions proposées |
| courriers/ | Modèles et rendus |
| db/ | Persistance SQLite |
| ui/ | Interface Streamlit |

## Entrées / Sorties
Modules Python locaux ; aucune requête réseau à l’exécution.

## Règles et décisions
Code et noms de fichiers sans accents. 2026-11-23.

## Comment tester
`pytest -q`

## État d’avancement
- [x] Squelette créé — 2026-11-23

## Limites connues et prochaines étapes
Seul le moteur légal est implémenté en phase 1.
