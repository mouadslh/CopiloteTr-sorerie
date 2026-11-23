# Journal

## 2026-11-23

- Création du squelette, des README obligatoires, des documents transversaux, de la configuration Python et du `.gitignore` (phase 0).
- Ajout des paramètres YAML datés, du moteur légal pur avec traces et des tests de limites et d'acceptation Atlas (phase 1).
- Validation : installation éditable avec dépendances de développement réussie dans `.venv` ; `pytest -q` — 13 tests réussis ; `ruff check .` — réussi.
- Le porteur du projet a confirmé l'adoption des hypothèses de `docs/A_VALIDER.md` pour le prototype ; la confirmation est consignée avec son périmètre.
- Phase 2 : ajout du schéma SQLite et du dépôt avec audit, validation Pydantic, imports CSV/XLSX/UBL, profils payeurs pondérés et génération déterministe du jeu Atlas fictif.
- Validation phase 2 : `pytest -q` — 27 tests réussis ; `ruff check .` — réussi. Le jeu central contient 35 lignes source (18 factures, 15 paiements, 2 flux), avant les clients dérivés.
