# Architecture

```text
Fichiers locaux ──> ingestion ──> validation humaine ──> db (SQLite)
                                               │
                       legal <── paramètres YAML ┘
                         │
       payeurs ──> simulation ──> actions ──> courriers
                         │
                       ui (Streamlit)
```

Le moteur légal de phase 1 est composé de fonctions pures : ses paramètres lui sont transmis explicitement et ses sorties incluent une trace de la version utilisée. Aucun module ne contacte un service réseau à l'exécution.
