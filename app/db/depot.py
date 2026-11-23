"""Depot SQLite local avec requetes parametrees et audit."""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Self

from app.ingestion.champs import FactureEntree, FluxPrevuEntree, PaiementEntree
from app.legal.moteur import ParametresLegaux


class DepotSQLite:
    """Acces simple et transactionnel a la base locale."""

    def __init__(self, chemin: str | Path) -> None:
        self.chemin = Path(chemin)
        if str(self.chemin) != ":memory:":
            self.chemin.parent.mkdir(parents=True, exist_ok=True)
        self.connexion = sqlite3.connect(str(self.chemin))
        self.connexion.row_factory = sqlite3.Row
        self.connexion.execute("PRAGMA foreign_keys = ON")

    def fermer(self) -> None:
        """Ferme la connexion SQLite."""
        self.connexion.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.fermer()

    def creer_schema(self) -> None:
        """Cree les tables definies dans schema.sql."""
        chemin_schema = Path(__file__).with_name("schema.sql")
        self.connexion.executescript(chemin_schema.read_text(encoding="utf-8"))
        self.connexion.commit()

    def _audit(self, objet: str, identifiant: str, operation: str, details: dict[str, Any]) -> None:
        self.connexion.execute(
            "INSERT INTO audit(type_objet, identifiant_objet, operation, details) VALUES (?, ?, ?, ?)",
            (objet, identifiant, operation, json.dumps(details, ensure_ascii=False, sort_keys=True, default=str)),
        )

    def ajouter_entreprise(self, nom: str, ville: str, date_reference: date, solde_initial: Decimal) -> None:
        """Ajoute le contexte de tresorerie de l'entreprise."""
        self.connexion.execute(
            "INSERT INTO entreprise(id, nom, ville, date_reference, solde_initial) VALUES (1, ?, ?, ?, ?)",
            (nom, ville, date_reference.isoformat(), str(solde_initial)),
        )
        self.connexion.commit()

    def ajouter_client(self, ice: str, nom: str, secteur: str = "inconnu") -> None:
        """Ajoute un client sans remplacer silencieusement un ICE existant."""
        self.connexion.execute(
            "INSERT INTO client(ice, nom, secteur) VALUES (?, ?, ?)", (ice, nom, secteur)
        )
        self.connexion.commit()

    def ajouter_facture(self, facture: FactureEntree) -> None:
        """Insere facture et client associe, puis trace la creation."""
        with self.connexion:
            self.connexion.execute(
                "INSERT INTO client(ice, nom, secteur) VALUES (?, ?, ?) "
                "ON CONFLICT(ice) DO UPDATE SET nom=excluded.nom, secteur=excluded.secteur",
                (facture.client_ice, facture.client_nom, facture.secteur),
            )
            self.connexion.execute(
                """INSERT INTO facture(numero, client_ice, date_facture, montant_ht, montant_tva,
                   montant_ttc, delai_conventionnel_jours, statut) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    facture.numero,
                    facture.client_ice,
                    facture.date_facture.isoformat(),
                    str(facture.montant_ht),
                    str(facture.montant_tva),
                    str(facture.montant_ttc),
                    facture.delai_conventionnel_jours,
                    facture.statut,
                ),
            )
            self._audit("facture", facture.numero, "creation", facture.model_dump(mode="json"))

    def modifier_facture(self, numero: str, changements: dict[str, Any]) -> None:
        """Met a jour des champs autorises et ecrit une trace d'audit."""
        autorises = {
            "client_nom", "client_ice", "secteur", "date_facture", "montant_ht",
            "montant_tva", "montant_ttc", "delai_conventionnel_jours", "statut",
        }
        inconnus = set(changements) - autorises
        if inconnus:
            raise ValueError(f"Champs de modification non autorises : {', '.join(sorted(inconnus))}")
        ligne = self.connexion.execute(
            """SELECT f.numero, c.nom AS client_nom, f.client_ice, c.secteur, f.date_facture,
               f.montant_ht, f.montant_tva, f.montant_ttc, f.delai_conventionnel_jours, f.statut
               FROM facture f JOIN client c ON c.ice=f.client_ice WHERE f.numero=?""",
            (numero,),
        ).fetchone()
        if ligne is None:
            raise ValueError(f"Facture introuvable : {numero}")
        donnees = dict(ligne)
        donnees.update(changements)
        validee = FactureEntree.model_validate(donnees)
        with self.connexion:
            self.connexion.execute(
                "INSERT INTO client(ice, nom, secteur) VALUES (?, ?, ?) "
                "ON CONFLICT(ice) DO UPDATE SET nom=excluded.nom, secteur=excluded.secteur",
                (validee.client_ice, validee.client_nom, validee.secteur),
            )
            self.connexion.execute(
                """UPDATE facture SET client_ice=?, date_facture=?, montant_ht=?, montant_tva=?,
                   montant_ttc=?, delai_conventionnel_jours=?, statut=? WHERE numero=?""",
                (
                    validee.client_ice, validee.date_facture.isoformat(), str(validee.montant_ht),
                    str(validee.montant_tva), str(validee.montant_ttc),
                    validee.delai_conventionnel_jours, validee.statut, numero,
                ),
            )
            self._audit("facture", numero, "modification", changements)

    def ajouter_paiement(self, paiement: PaiementEntree) -> None:
        """Ajoute un paiement valide associe a une facture."""
        facture = self.connexion.execute(
            "SELECT date_facture FROM facture WHERE numero=?", (paiement.numero_facture,)
        ).fetchone()
        if facture is None:
            raise ValueError(f"Facture introuvable : {paiement.numero_facture}")
        if paiement.date_paiement < date.fromisoformat(facture["date_facture"]):
            raise ValueError("La date de paiement ne peut pas preceder celle de la facture.")
        with self.connexion:
            self.connexion.execute(
                "INSERT INTO paiement(facture_numero, date_paiement, montant) VALUES (?, ?, ?)",
                (paiement.numero_facture, paiement.date_paiement.isoformat(), str(paiement.montant)),
            )

    def ajouter_flux(self, flux: FluxPrevuEntree) -> None:
        """Ajoute un flux prevu date."""
        self.connexion.execute(
            "INSERT INTO flux_prevu(libelle, date_flux, montant) VALUES (?, ?, ?)",
            (flux.libelle, flux.date_flux.isoformat(), str(flux.montant)),
        )
        self.connexion.commit()

    def ajouter_parametre(self, parametres: ParametresLegaux) -> None:
        """Ajoute ou remplace une version legale et journalise le changement."""
        donnees = {
            "effet_a_partir_du": parametres.effet_a_partir_du.isoformat(),
            "delai_defaut_jours": parametres.delai_defaut_jours,
            "plafond_conventionnel_jours": parametres.plafond_conventionnel_jours,
            "plafond_sectoriel_jours": parametres.plafond_sectoriel_jours,
            "taux_directeur": str(parametres.taux_directeur),
            "majoration_par_mois_sup": str(parametres.majoration_par_mois_sup),
        }
        existant = self.connexion.execute(
            "SELECT 1 FROM parametre_legal WHERE effet_a_partir_du=?",
            (donnees["effet_a_partir_du"],),
        ).fetchone()
        operation = "modification" if existant else "creation"
        with self.connexion:
            self.connexion.execute(
                """INSERT INTO parametre_legal(effet_a_partir_du, delai_defaut_jours,
                   plafond_conventionnel_jours, plafond_sectoriel_jours, taux_directeur,
                   majoration_par_mois_sup) VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(effet_a_partir_du) DO UPDATE SET
                   delai_defaut_jours=excluded.delai_defaut_jours,
                   plafond_conventionnel_jours=excluded.plafond_conventionnel_jours,
                   plafond_sectoriel_jours=excluded.plafond_sectoriel_jours,
                   taux_directeur=excluded.taux_directeur,
                   majoration_par_mois_sup=excluded.majoration_par_mois_sup""",
                tuple(donnees.values()),
            )
            self._audit("parametre_legal", donnees["effet_a_partir_du"], operation, donnees)
