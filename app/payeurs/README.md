# payeurs

## But
Calculer les profils de retard des clients à partir de l’historique.

## Contenu
| Fichier | Rôle |
|---|---|
| profil.py | Retard médian pondéré, quantiles 25/75 et alerte d'historique insuffisant |

## Entrées / Sorties
Factures payées et date d'échéance estimée vers un profil déterministe ; poids croissants avec la récence.

## Règles et décisions
Moins de 5 paiements utilise le retard médian sectoriel fourni et ajoute une alerte. Les quantiles sont des quantiles empiriques pondérés. 2026-11-23.

## Comment tester
`pytest -q`

## État d’avancement
- [x] Profil payeur initial implémenté — 2026-11-23

## Limites connues et prochaines étapes
Valeur sectorielle à fournir par l'appelant ; aucune base de statistiques sectorielles n'est incluse.
