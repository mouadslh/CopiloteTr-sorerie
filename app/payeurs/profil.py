"""Statistiques simples et deterministes de retard client."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.legal.moteur import ParametresLegaux, echeance_legale


class HistoriquePaiement(BaseModel):
    """Facture payee utilisee dans le calcul du profil."""

    model_config = ConfigDict(frozen=True)

    date_facture: date
    date_paiement: date
    delai_conventionnel_jours: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def verifier_dates(self) -> HistoriquePaiement:
        """Refuse un paiement date avant l'emission de la facture."""
        if self.date_paiement < self.date_facture:
            raise ValueError("La date de paiement ne peut pas preceder celle de la facture.")
        return self


class ProfilPayeur(BaseModel):
    """Resume des retards historiques avec alertes de confiance."""

    retard_median_jours: int
    quantile_75_jours: int
    quantile_25_jours: int
    nombre_factures_payees: int
    historique_insuffisant: bool
    alerte: str | None = None


def _quantile_pondere(valeurs: list[tuple[int, int]], quantile: float) -> int:
    """Quantile empirique pondere, poids croissants avec la recence."""
    if not valeurs:
        return 0
    total = sum(poids for _, poids in valeurs)
    seuil = quantile * total
    cumule = 0
    for valeur, poids in sorted(valeurs, key=lambda element: element[0]):
        cumule += poids
        if cumule >= seuil:
            return valeur
    return max(valeur for valeur, _ in valeurs)


def calculer_profil(
    historique: list[HistoriquePaiement],
    parametres: ParametresLegaux,
    *,
    retard_median_sectoriel: int = 0,
) -> ProfilPayeur:
    """Calcule retard median, quantiles et alerte sous cinq paiements."""
    if retard_median_sectoriel < 0:
        raise ValueError("Le retard sectoriel ne peut pas etre negatif.")
    if len(historique) < 5:
        return ProfilPayeur(
            retard_median_jours=retard_median_sectoriel,
            quantile_75_jours=retard_median_sectoriel,
            quantile_25_jours=retard_median_sectoriel,
            nombre_factures_payees=len(historique),
            historique_insuffisant=True,
            alerte="Historique insuffisant : retard median sectoriel utilise.",
        )
    retards_recents: list[tuple[int, int]] = []
    for poids, entree in enumerate(sorted(historique, key=lambda item: item.date_facture), start=1):
        echeance = echeance_legale(
            entree.date_facture, parametres, entree.delai_conventionnel_jours
        ).valeur
        retard = (entree.date_paiement - echeance).days
        retards_recents.append((retard, poids))
    return ProfilPayeur(
        retard_median_jours=_quantile_pondere(retards_recents, 0.50),
        quantile_75_jours=_quantile_pondere(retards_recents, 0.75),
        quantile_25_jours=_quantile_pondere(retards_recents, 0.25),
        nombre_factures_payees=len(historique),
        historique_insuffisant=False,
    )
