"""Tests d'import CSV/XLSX/UBL et de validation des champs."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from pydantic import ValidationError

from app.ingestion.champs import FactureEntree
from app.ingestion.excel import importer_factures, importer_flux, importer_paiements
from app.ingestion.ubl import importer_ubl
from data.generer_demo import generer


def test_csv_et_mappage_colonnes(tmp_path: Path) -> None:
    fichier = tmp_path / "factures.csv"
    fichier.write_text(
        "numero,client_nom,client_ice,date_facture,montant_ht,montant_tva,montant_ttc\n"
        "F-1,Client Test,001234567890123,2026-01-01,100.00,20.00,120.00\n",
        encoding="utf-8",
    )
    facture = importer_factures(fichier)[0]
    assert facture.numero == "F-1"
    assert str(facture.montant_ttc) == "120.00"
    autre = tmp_path / "alias.csv"
    autre.write_text(
        "N,Nom,ICE,Date,HT,TVA,TTC\nF-2,Client Test,001234567890123,2026-01-01,100,20,120\n",
        encoding="utf-8",
    )
    assert importer_factures(
        autre,
        {
            "numero": "N", "client_nom": "Nom", "client_ice": "ICE", "date_facture": "Date",
            "montant_ht": "HT", "montant_tva": "TVA", "montant_ttc": "TTC",
        },
    )[0].numero == "F-2"


def test_import_csv_paiement_et_flux(tmp_path: Path) -> None:
    paiements = tmp_path / "paiements.csv"
    paiements.write_text(
        "numero_facture,date_paiement,montant\nF-1,2026-02-01,120.00\n", encoding="utf-8"
    )
    assert importer_paiements(paiements)[0].montant == 120
    flux = tmp_path / "flux.csv"
    flux.write_text("libelle,date_flux,montant\nBois,2026-11-20,-70000.00\n", encoding="utf-8")
    assert importer_flux(flux)[0].montant == -70000


def test_validation_ice_montants_et_coherence() -> None:
    base = {
        "numero": "F-1", "client_nom": "Client", "client_ice": "001234567890123",
        "date_facture": "2026-01-01", "montant_ht": "100", "montant_tva": "20", "montant_ttc": "120",
    }
    assert FactureEntree.model_validate(base).montant_ttc > 0
    with pytest.raises(ValidationError, match="ICE"):
        FactureEntree.model_validate({**base, "client_ice": "123"})
    with pytest.raises(ValidationError):
        FactureEntree.model_validate({**base, "montant_ht": "0"})
    with pytest.raises(ValidationError, match=r"HT \+ TVA"):
        FactureEntree.model_validate({**base, "montant_ttc": "119"})


def test_factures_bruitees_rejetees(tmp_path: Path) -> None:
    generer(tmp_path)
    with pytest.raises(ValidationError, match=r"HT \+ TVA"):
        importer_factures(tmp_path / "factures_bruitees.csv")


def test_import_excel_xlsx(tmp_path: Path) -> None:
    fichier = tmp_path / "minimal.xlsx"
    workbook = '''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>
      <sheet name="Factures" sheetId="1" r:id="rId1"/></sheets></workbook>'''
    relations = '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
      <Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>'''
    cells = [
        ["numero", "client_nom", "client_ice", "date_facture", "montant_ht", "montant_tva", "montant_ttc"],
        ["F-XLSX", "Client Excel", "001234567890123", "2026-01-01", "100", "20", "120"],
    ]
    xml_rows = []
    for row_num, row in enumerate(cells, start=1):
        xml_cells = "".join(
            f'<c r="{chr(65 + col)}{row_num}" t="inlineStr"><is><t>{val}</t></is></c>'
            for col, val in enumerate(row)
        )
        xml_rows.append(f'<row r="{row_num}">{xml_cells}</row>')
    sheet = (
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
        + "".join(xml_rows) + "</sheetData></worksheet>"
    )
    with ZipFile(fichier, "w", ZIP_DEFLATED) as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", relations)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
    assert importer_factures(fichier, feuille="Factures")[0].numero == "F-XLSX"


def test_import_ubl_demo(tmp_path: Path) -> None:
    generer(tmp_path)
    facture = importer_ubl(tmp_path / "exemple_ubl.xml")
    assert facture.numero == "UBL-AT-001"
    assert facture.client_ice == "004567890123456"
    assert facture.delai_conventionnel_jours == 45
