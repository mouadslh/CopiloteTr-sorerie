from datetime import date
from decimal import Decimal

import pytest

from app.legal.moteur import (
    amende,
    charger_parametres,
    clause_hors_plafond,
    echeance_legale,
    mois_de_retard,
    selectionner_parametres,
)

PARAMS = charger_parametres()
P = selectionner_parametres(date(2026, 11, 9), PARAMS)


def test_selection_parametre_date_effet() -> None:
    assert selectionner_parametres(date(2026, 11, 9), PARAMS) == PARAMS[0]


def test_echeances_atlas_et_delai_par_defaut() -> None:
    assert echeance_legale(date(2026, 8, 15), P, 90).valeur == date(2026, 11, 13)
    assert echeance_legale(date(2026, 9, 1), P).valeur == date(2026, 10, 31)


def test_jour_exact_et_paiement_avant_echeance() -> None:
    assert mois_de_retard(date(2026, 10, 31), date(2026, 10, 31), P).valeur == 0
    assert mois_de_retard(date(2026, 10, 31), date(2026, 10, 30), P).valeur == 0
    assert mois_de_retard(date(2026, 10, 31), date(2026, 11, 1), P).valeur == 1
    assert mois_de_retard(date(2026, 10, 31), date(2026, 11, 30), P).valeur == 1
    assert mois_de_retard(date(2026, 10, 31), date(2026, 12, 1), P).valeur == 2


def test_plafond_inclus_et_clause_hors_plafond() -> None:
    assert clause_hors_plafond(120, P).valeur is None
    resultat = clause_hors_plafond(150, P).valeur
    assert resultat is not None
    assert "150 > 120" in resultat
    assert "sauf secteur à 180 j, à vérifier" in resultat
    assert clause_hors_plafond(180, P, secteur_a_180_jours=True).valeur is None


@pytest.mark.parametrize(
    ("mois", "attendu"),
    [(1, "1350.00"), (2, "1860.00"), (3, "2370.00")],
)
def test_amende_atlas(mois: int, attendu: str) -> None:
    resultat = amende(Decimal(60000), mois, P)
    assert resultat.valeur == Decimal(attendu)
    assert resultat.trace.effet_a_partir_du == date(2026, 1, 1)


def test_annee_bissextile_et_traces() -> None:
    resultat = echeance_legale(
        date(2024, 2, 29), P, 1
    )
    assert resultat.valeur == date(2024, 3, 1)
    assert resultat.trace.parametre == "delai_conventionnel_jours"
    assert resultat.trace.effet_a_partir_du == date(2026, 1, 1)


def test_valeurs_invalides() -> None:
    with pytest.raises(ValueError):
        echeance_legale(date(2026, 1, 1), P, -1)
    with pytest.raises(ValueError):
        amende(Decimal(1), -1, P)


def test_amende_nulle_sans_retard() -> None:
    assert amende(Decimal(60000), 0, P).valeur == Decimal("0.00")


def test_trace_clause_et_retard() -> None:
    clause = clause_hors_plafond(150, P)
    retard = mois_de_retard(date(2026, 10, 31), date(2026, 11, 9), P)
    assert clause.trace.parametre == "plafond_conventionnel_jours"
    assert retard.valeur == 1
    assert retard.trace.parametre == "jours_de_retard"
