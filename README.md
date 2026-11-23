# Copilote de tresorerie pour PME marocaines

Outil local et deterministe pour estimer les echeances, retards et projections de tresorerie. Les parametres juridiques sont versionnes en YAML. Les resultats sont des estimations, pas un conseil juridique ou fiscal.

## Installation et lancement

```bash
python -m venv .venv
source .venv/bin/activate && pip install -e .
streamlit run app/ui/tableau_de_bord.py
```

## Structure

- [docs/README.md](docs/README.md) — documentation transversale
- [app/README.md](app/README.md) — modules applicatifs
- [app/legal/README.md](app/legal/README.md) — moteur légal
- [app/ingestion/README.md](app/ingestion/README.md) — import
- [app/payeurs/README.md](app/payeurs/README.md) — profils payeurs
- [app/simulation/README.md](app/simulation/README.md) — projections
- [app/actions/README.md](app/actions/README.md) — recommandations
- [app/courriers/README.md](app/courriers/README.md) — courriers
- [app/db/README.md](app/db/README.md) — SQLite
- [app/ui/README.md](app/ui/README.md) — interface
- [data/README.md](data/README.md) — jeu fictif
- [tests/README.md](tests/README.md) — vérifications
- [sorties/README.md](sorties/README.md) — exports

## État

Phases 0 à 2 : squelette, moteur légal, stockage SQLite, imports CSV/XLSX/UBL, profils payeurs et jeu Atlas fictif. Voir [docs/PLAN.md](docs/PLAN.md).
