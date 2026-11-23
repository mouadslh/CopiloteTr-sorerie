"""Tests d'acceptation des seules lignes pertinentes a la phase 1."""

from datetime import date
from decimal import Decimal

from app.legal.moteur import (
    amende,
    charger_parametres,
    clause_hors_plafond,
    echeance_legale,
    selectionner_parametres,
)

P = selectionner_parametres(date(2026, 11, 9), charger_parametres())


def test_atlas_echeances_et_clause() -> None:
    assert echeance_legale(date(2026, 8, 15), P, 90).valeur == date(2026, 11, 13)
    assert echeance_legale(date(2026, 9, 1), P).valeur == date(2026, 10, 31)
    clause = clause_hors_plafond(150, P).valeur
    assert clause is not None and "sauf secteur à 180 j, à vérifier" in clause


def test_atlas_amendes_b() -> None:
    assert amende(Decimal(60000), 1, P).valeur == Decimal("1350.00")
    assert amende(Decimal(60000), 2, P).valeur == Decimal("1860.00")
    assert amende(Decimal(60000), 3, P).valeur == Decimal("2370.00")
