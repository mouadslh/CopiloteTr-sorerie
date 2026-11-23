# Décisions techniques

## 2026-11-23 — Noms des paramètres légaux

- Contexte : le cadrage mélange `majoration_par_mois_sup` et `majoration_mensuelle`, ainsi que `delai_defaut_jours` et `delai_defaut`.
- Choix : les noms YAML canoniques sont `majoration_par_mois_sup` et `delai_defaut_jours` ; le code les utilise sans alias.
- Alternatives rejetées : garder des alias implicites, qui cacheraient les écarts de configuration.

## 2026-11-23 — Résultats avec traçabilité

- Contexte : chaque calcul légal doit expliquer règle, paramètre et date d'effet.
- Choix : les fonctions retournent des objets typés contenant valeur et `TraceLegale` ; les paramètres sont chargés explicitement et la trace identifie leur date d'effet.
- Alternatives rejetées : état global et accès fichier depuis les fonctions pures.

## 2026-11-23 — Mois de retard et arrondi

- Contexte : convention temporaire définie par le prompt.
- Choix : mois entamé = plafond du nombre de jours divisé par 30 ; aucun mois de retard produit une amende nulle ; amende monétaire arrondie à 2 décimales avec `ROUND_HALF_UP`.
- Alternatives rejetées : calculs en float ou mois calendaires implicites.
