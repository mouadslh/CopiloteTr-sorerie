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

## 2026-11-23 — Lecture Excel sans moteur supplementaire

- Contexte : le MVP autorise pandas mais limite les dependances et ne liste pas openpyxl.
- Choix : CSV via pandas et XLSX via une lecture locale minimale avec `zipfile` et XML de la bibliotheque standard ; seuls les fichiers `.xlsx` sont pris en charge.
- Alternatives rejetees : ajouter openpyxl/xlrd au MVP ou convertir des montants en float lors de l'import.

## 2026-11-23 — Donnees et audit

- Contexte : SQLite, traçabilite et jeu de demonstration reduit.
- Choix : les montants sont stockes en texte decimal dans SQLite ; les ajouts/modifications de facture et de parametre ecrivent une entree d'audit. Le jeu central comporte 35 lignes CSV.
- Alternatives rejetees : stocker les montants en REAL ou inclure les factures de validation bruitées dans le jeu importe automatiquement.

## 2026-11-23 — Retards payes avant echeance

- Contexte : le retard est defini comme date de paiement moins echeance legale.
- Choix : conserver les retards negatifs lorsqu'un paiement intervient avant l'echeance ; les profils ne tronquent pas les paiements anticipes a zero.
- Alternatives rejetees : borner tous les retards a zero, ce qui ferait perdre l'information de paiement anticipe.
