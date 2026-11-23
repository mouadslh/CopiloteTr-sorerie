# Copilote de trésorerie pour PME marocaines

## Présentation du projet

Le Copilote de trésorerie est un prototype d’outil local destiné aux petites et moyennes entreprises marocaines. Il vise à aider une entreprise à comprendre quand ses factures devraient être payées, à repérer les retards récurrents de ses clients et, dans les prochaines phases, à anticiper les périodes où sa trésorerie pourrait devenir insuffisante.

Le projet est conçu pour traiter les données sur la machine de l’entreprise : il n’utilise pas de modèle d’intelligence artificielle ni d’API externe à l’exécution. Ses calculs s’appuient sur des règles explicites et des paramètres modifiables.

## Problématique

Une entreprise peut être rentable tout en manquant temporairement de liquidités. Elle doit payer ses fournisseurs, ses salaires et ses autres dépenses à des dates précises, tandis que les règlements de ses clients peuvent arriver en retard. Quand les factures, les dates de paiement et les dépenses prévues sont suivies séparément, il devient difficile de voir assez tôt l’ampleur d’un décalage de trésorerie et de décider quel client relancer en premier.

Le projet s’attaque à trois difficultés liées :

- suivre les échéances de paiement et repérer les clauses de délai qui dépassent les paramètres configurés ;
- mesurer le comportement de paiement à partir de l’historique de chaque client ;
- réunir les informations nécessaires pour prévoir les encaissements et décaissements à venir.

## Solution proposée

Le Copilote rassemble les factures, paiements et flux prévus dans un outil unique. Il calcule des échéances et des retards estimés, garde une trace des paramètres utilisés et construit un profil simple de comportement de paiement pour chaque client.

La feuille de route prévoit ensuite une simulation de trésorerie sur 13 semaines, des actions à prioriser et des modèles de courriers de relance. Ces propositions resteront vérifiables par une personne : le logiciel ne doit pas envoyer automatiquement de courriers ni remplacer la décision du dirigeant.

## Fonctionnement prévu

1. **Importer les données** depuis des fichiers CSV, Excel XLSX ou des factures XML au format UBL.
2. **Valider les informations** : format de l’ICE, montants, dates et cohérence entre HT, TVA et TTC.
3. **Enregistrer les données** dans une base SQLite locale et conserver un journal des changements de factures et de paramètres.
4. **Calculer les échéances et retards estimés** à l’aide de règles déterministes et de paramètres versionnés en YAML.
5. **Établir un profil client** à partir des paiements passés ; lorsqu’il y a moins de cinq paiements, signaler que l’historique est insuffisant et utiliser une valeur sectorielle fournie.
6. **Dans les prochaines phases**, simuler les soldes jour par jour sur 13 semaines, comparer plusieurs scénarios et préparer des actions ou des brouillons de relance.

## État d’avancement

Les phases 0 à 2 sont réalisées :

- **Phase 0 — Squelette et documentation :** structure du projet, configuration Python et documentation de suivi.
- **Phase 1 — Moteur légal :** échéances, clauses hors plafond, mois de retard, amendes estimées et traces de paramètres.
- **Phase 2 — Données et profils :** SQLite, audit, validation Pydantic, imports CSV/XLSX/UBL, profils payeurs et données fictives de démonstration.

Les phases restantes sont la simulation de trésorerie (phase 3), les recommandations et courriers (phase 4), l’extraction PDF et l’écran de validation (phase 5), puis le tableau de bord (phase 6). **L’interface Streamlit n’est donc pas encore disponible.** L’avancement détaillé se trouve dans [docs/PLAN.md](docs/PLAN.md).

## Installation et vérifications

Python 3.11 ou une version plus récente est requis. Depuis la racine du projet :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Générer le jeu fictif et lancer les vérifications :

```bash
python3 data/generer_demo.py
pytest -q
ruff check .
```

Le jeu « Menuiserie Atlas » est entièrement fictif. Son scénario comporte 18 factures, 15 paiements et 2 flux prévus ; deux lignes supplémentaires volontairement invalides servent à vérifier les contrôles d’import. Le générateur utilise une graine fixe pour produire des résultats reproductibles.

## Paramètres et limites d’interprétation

Les paramètres du moteur sont dans [app/legal/parametres.yaml](app/legal/parametres.yaml). Les dates de départ, plafonds, taux et méthodes de calcul sont les hypothèses adoptées pour le prototype et consignées dans [docs/A_VALIDER.md](docs/A_VALIDER.md). Leur adoption permet de développer et tester le logiciel ; elle ne constitue pas une vérification indépendante du droit applicable.

Les échéances et amendes produites sont des **estimations**, pas un conseil juridique ou fiscal. Les résultats et les éventuels courriers devront être vérifiés par une personne compétente avant tout usage réel. Le jeu de démonstration ne contient aucune donnée de client réelle.

## Architecture du dépôt

| Dossier | Rôle |
|---|---|
| [app/legal](app/legal/README.md) | Calculs déterministes et paramètres légaux versionnés |
| [app/ingestion](app/ingestion/README.md) | Validation des données et imports CSV/XLSX/UBL |
| [app/db](app/db/README.md) | Stockage SQLite et audit |
| [app/payeurs](app/payeurs/README.md) | Profils et retards historiques des clients |
| [app/simulation](app/simulation/README.md) | Module prévu pour les projections de trésorerie |
| [app/actions](app/actions/README.md) | Module prévu pour les actions prioritaires |
| [app/courriers](app/courriers/README.md) | Module prévu pour les brouillons de relance |
| [app/ui](app/ui/README.md) | Interface Streamlit prévue |
| [data](data/README.md) | Générateur et données fictives de démonstration |
| [tests](tests/README.md) | Tests automatisés |
| [docs](docs/README.md) | Plan, journal, décisions, glossaire et architecture |
| [sorties](sorties/README.md) | Destination prévue des exports |

## Résumé pour la présentation

> Le Copilote de trésorerie est un prototype local pour PME marocaines. Il centralise les factures, les paiements et les dépenses prévues, estime les échéances et les retards, et décrit les habitudes de règlement des clients. Son objectif final est d’aider l’entreprise à prévoir ses besoins de liquidités sur 13 semaines et à préparer des relances. Les calculs sont déterministes, les paramètres sont traçables et les données de démonstration sont fictives.
