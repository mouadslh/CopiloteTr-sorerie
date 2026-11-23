"""Moteur pur d'estimation des echeances et amendes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Generic, TypeVar

import yaml

T = TypeVar("T")


@dataclass(frozen=True)
class ParametresLegaux:
    """Parametres legaux applicables a partir d'une date."""

    effet_a_partir_du: date
    delai_defaut_jours: int
    plafond_conventionnel_jours: int
    plafond_sectoriel_jours: int
    taux_directeur: Decimal
    majoration_par_mois_sup: Decimal


@dataclass(frozen=True)
class TraceLegale:
    """Origine des parametres utilises par un resultat."""

    regle: str
    parametre: str
    valeur_parametre: str
    effet_a_partir_du: date


@dataclass(frozen=True)
class ResultatLegal(Generic[T]):
    """Valeur calculee et trace correspondante."""

    valeur: T
    trace: TraceLegale


def charger_parametres(chemin: str | Path | None = None) -> tuple[ParametresLegaux, ...]:
    """Charge les versions YAML et les trie par date d'effet."""
    fichier = Path(chemin) if chemin else Path(__file__).with_name("parametres.yaml")
    with fichier.open(encoding="utf-8") as flux:
        brut = yaml.safe_load(flux) or {}
    versions = tuple(
        ParametresLegaux(
            effet_a_partir_du=date.fromisoformat(item["effet_a_partir_du"]),
            delai_defaut_jours=int(item["delai_defaut_jours"]),
            plafond_conventionnel_jours=int(item["plafond_conventionnel_jours"]),
            plafond_sectoriel_jours=int(item["plafond_sectoriel_jours"]),
            taux_directeur=Decimal(str(item["taux_directeur"])),
            majoration_par_mois_sup=Decimal(str(item["majoration_par_mois_sup"])),
        )
        for item in brut.get("versions", [])
    )
    if not versions:
        raise ValueError("Aucun parametre legal n'est configure.")
    return tuple(sorted(versions, key=lambda p: p.effet_a_partir_du))


def selectionner_parametres(
    date_application: date,
    versions: tuple[ParametresLegaux, ...],
) -> ParametresLegaux:
    """Retourne la derniere version dont la date d'effet est atteinte."""
    eligibles = [p for p in versions if p.effet_a_partir_du <= date_application]
    if not eligibles:
        raise ValueError(f"Aucun parametre legal applicable au {date_application.isoformat()}.")
    return max(eligibles, key=lambda p: p.effet_a_partir_du)


def echeance_legale(
    date_depart: date,
    parametres: ParametresLegaux,
    delai_conventionnel_jours: int | None = None,
) -> ResultatLegal[date]:
    """Calcule une echeance estimee depuis la date de depart fournie."""
    p = parametres
    delai = p.delai_defaut_jours if delai_conventionnel_jours is None else delai_conventionnel_jours
    if delai < 0:
        raise ValueError("Le delai conventionnel ne peut pas etre negatif.")
    valeur = date_depart + timedelta(days=delai)
    origine = "delai_defaut_jours" if delai_conventionnel_jours is None else "delai_conventionnel_jours"
    return ResultatLegal(valeur, TraceLegale("date_depart + delai en jours", origine, str(delai), p.effet_a_partir_du))


def clause_hors_plafond(
    delai_conventionnel_jours: int,
    parametres: ParametresLegaux,
    *,
    secteur_a_180_jours: bool = False,
) -> ResultatLegal[str | None]:
    """Signale une clause au-dela du plafond conventionnel ou sectoriel."""
    p = parametres
    plafond = p.plafond_sectoriel_jours if secteur_a_180_jours else p.plafond_conventionnel_jours
    if delai_conventionnel_jours < 0:
        raise ValueError("Le delai conventionnel ne peut pas etre negatif.")
    hors = delai_conventionnel_jours > plafond
    valeur = None if not hors else f"Clause hors plafond ({delai_conventionnel_jours} > {plafond} jours)"
    if hors and not secteur_a_180_jours:
        valeur += "; sauf secteur à 180 j, à vérifier"
    parametre = "plafond_sectoriel_jours" if secteur_a_180_jours else "plafond_conventionnel_jours"
    return ResultatLegal(valeur, TraceLegale("comparaison stricte au plafond", parametre, str(plafond), p.effet_a_partir_du))


def mois_de_retard(
    echeance: date,
    date_paiement: date,
    parametres: ParametresLegaux,
) -> ResultatLegal[int]:
    """Compte les mois de 30 jours entames ; un paiement a temps vaut zero."""
    p = parametres
    jours = max(0, (date_paiement - echeance).days)
    mois = (jours + 29) // 30
    return ResultatLegal(mois, TraceLegale("ceil(jours_de_retard / 30)", "jours_de_retard", str(jours), p.effet_a_partir_du))


def amende(
    montant: Decimal,
    mois: int,
    parametres: ParametresLegaux,
) -> ResultatLegal[Decimal]:
    """Estime l'amende avec taux progressif et arrondi monetaire a deux decimales."""
    if montant < 0:
        raise ValueError("Le montant ne peut pas etre negatif.")
    if mois < 0:
        raise ValueError("Le nombre de mois ne peut pas etre negatif.")
    p = parametres
    taux = p.taux_directeur + p.majoration_par_mois_sup * max(0, mois - 1)
    valeur = Decimal("0.00") if mois == 0 else (montant * taux).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    trace = TraceLegale(
        "zero si aucun mois de retard, sinon montant * (taux_directeur + majoration_par_mois_sup * max(0, mois - 1))",
        "taux_directeur + majoration_par_mois_sup",
        f"{p.taux_directeur} + {p.majoration_par_mois_sup}; mois={mois}",
        p.effet_a_partir_du,
    )
    return ResultatLegal(valeur, trace)
