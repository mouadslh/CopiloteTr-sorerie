"""Modeles Pydantic pour valider les donnees de facture importees."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class FactureEntree(BaseModel):
    """Facture normalisee avant insertion dans la base locale."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    numero: str = Field(min_length=1, max_length=100)
    client_nom: str = Field(min_length=1, max_length=200)
    client_ice: str
    secteur: str = Field(default="inconnu", max_length=100)
    date_facture: date
    montant_ht: Decimal = Field(gt=0)
    montant_tva: Decimal = Field(ge=0)
    montant_ttc: Decimal = Field(gt=0)
    delai_conventionnel_jours: int | None = Field(default=None, ge=0)
    statut: str = "impayee"

    @field_validator("client_ice")
    @classmethod
    def valider_ice(cls, valeur: str) -> str:
        if len(valeur) != 15 or not valeur.isdigit():
            raise ValueError("L'ICE doit contenir exactement 15 chiffres.")
        return valeur

    @field_validator("delai_conventionnel_jours", mode="before")
    @classmethod
    def normaliser_delai_vide(cls, valeur: object) -> object:
        """Traite une cellule vide CSV comme absence de clause renseignee."""
        return None if valeur == "" else valeur

    @field_validator("statut")
    @classmethod
    def valider_statut(cls, valeur: str) -> str:
        if valeur not in {"impayee", "payee", "partiellement_payee"}:
            raise ValueError("Statut de facture non reconnu.")
        return valeur

    @model_validator(mode="after")
    def verifier_totaux(self) -> FactureEntree:
        if self.montant_ht + self.montant_tva != self.montant_ttc:
            raise ValueError("Le total TTC doit etre egal a HT + TVA.")
        return self


class PaiementEntree(BaseModel):
    """Paiement associe a une facture existante."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    numero_facture: str = Field(min_length=1, max_length=100)
    date_paiement: date
    montant: Decimal = Field(gt=0)


class FluxPrevuEntree(BaseModel):
    """Flux prevu, positif pour une entree et negatif pour une sortie."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    libelle: str = Field(min_length=1, max_length=200)
    date_flux: date
    montant: Decimal
