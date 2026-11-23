"""Tests de base de donnees, profil payeur et jeu Atlas phase 2."""

from dataclasses import replace
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from app.db.depot import DepotSQLite
from app.ingestion.champs import FactureEntree, PaiementEntree
from app.ingestion.excel import importer_factures
from app.legal.moteur import charger_parametres, selectionner_parametres
from app.payeurs.profil import HistoriquePaiement, calculer_profil
from data.generer_demo import generer


def test_depot_creation_audit_et_dates_coherentes(tmp_path: Path) -> None:
    with DepotSQLite(tmp_path / "demo.sqlite") as depot:
        depot.creer_schema()
        facture = FactureEntree.model_validate(
            {
                "numero": "DB-1", "client_nom": "Client O'Reilly", "client_ice": "001234567890123",
                "date_facture": "2026-01-01", "montant_ht": "100", "montant_tva": "20",
                "montant_ttc": "120", "statut": "impayee",
            }
        )
        depot.ajouter_facture(facture)
        depot.ajouter_paiement(
            PaiementEntree(numero_facture="DB-1", date_paiement=date(2026, 2, 1), montant="120")
        )
        with pytest.raises(ValueError, match="preceder"):
            depot.ajouter_paiement(
                PaiementEntree(numero_facture="DB-1", date_paiement=date(2025, 12, 31), montant="120")
            )
        depot.modifier_facture("DB-1", {"statut": "payee"})
        lignes = depot.connexion.execute(
            "SELECT operation FROM audit WHERE type_objet='facture' ORDER BY id"
        ).fetchall()
        assert [ligne["operation"] for ligne in lignes] == ["creation", "modification"]
        assert depot.connexion.execute("SELECT count(*) FROM paiement").fetchone()[0] == 1


def test_modification_parametre_auditee(tmp_path: Path) -> None:
    parametres = selectionner_parametres(date(2026, 11, 9), charger_parametres())
    with DepotSQLite(tmp_path / "params.sqlite") as depot:
        depot.creer_schema()
        depot.ajouter_parametre(parametres)
        depot.ajouter_parametre(replace(parametres, delai_defaut_jours=61))
        operations = depot.connexion.execute(
            "SELECT operation FROM audit WHERE type_objet='parametre_legal' ORDER BY id"
        ).fetchall()
        assert [ligne["operation"] for ligne in operations] == ["creation", "modification"]
        assert depot.connexion.execute("SELECT delai_defaut_jours FROM parametre_legal").fetchone()[0] == 61


def test_historique_insuffisant_alerte_sectorielle() -> None:
    parametres = selectionner_parametres(date(2026, 11, 9), charger_parametres())
    profil = calculer_profil(
        [HistoriquePaiement(date_facture=date(2026, 1, 1), date_paiement=date(2026, 3, 1))],
        parametres,
        retard_median_sectoriel=24,
    )
    assert profil.historique_insuffisant
    assert profil.retard_median_jours == 24
    assert "Historique insuffisant" in (profil.alerte or "")


def test_retard_negatif_si_paiement_avant_echeance() -> None:
    historique = [
        HistoriquePaiement(
            date_facture=date(2026, 1, 1),
            date_paiement=date(2026, 2, 1),
            delai_conventionnel_jours=60,
        )
        for _ in range(5)
    ]
    parametres = selectionner_parametres(date(2026, 11, 9), charger_parametres())
    assert calculer_profil(historique, parametres).retard_median_jours == -29


@pytest.mark.parametrize(("code", "attendu"), [("A", 35), ("B", 20), ("C", 10)])
def test_profil_demo_atlas(tmp_path: Path, code: str, attendu: int) -> None:
    generer(tmp_path)
    factures = importer_factures(tmp_path / "factures.csv")
    paiements = pd.read_csv(tmp_path / "paiements.csv", dtype=str).to_dict(orient="records")
    index_factures = {facture.numero: facture for facture in factures}
    historique = [
        HistoriquePaiement(
            date_facture=index_factures[paiement["numero_facture"]].date_facture,
            date_paiement=paiement["date_paiement"],
            delai_conventionnel_jours=index_factures[paiement["numero_facture"]].delai_conventionnel_jours,
        )
        for paiement in paiements
        if paiement["numero_facture"].startswith(f"AT-{code}-")
    ]
    parametres = selectionner_parametres(date(2026, 11, 9), charger_parametres())
    profil = calculer_profil(historique, parametres)
    assert profil.retard_median_jours == attendu
    assert not profil.historique_insuffisant
    assert profil.quantile_75_jours >= profil.retard_median_jours


def test_jeu_demo_reproductible_et_sous_40_lignes(tmp_path: Path) -> None:
    generer(tmp_path)
    premier = (tmp_path / "factures.csv").read_bytes()
    generer(tmp_path)
    assert (tmp_path / "factures.csv").read_bytes() == premier
    lignes = sum(
        max(0, len((tmp_path / nom).read_text(encoding="utf-8").splitlines()) - 1)
        for nom in ("factures.csv", "paiements.csv", "flux_prevus.csv")
    )
    assert lignes == 35
