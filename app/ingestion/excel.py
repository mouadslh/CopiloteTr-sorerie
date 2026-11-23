"""Import tabulaire CSV et XLSX avec mappage configurable, sans moteur externe."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, TypeVar
from zipfile import ZipFile

import pandas as pd
from pydantic import BaseModel

from app.ingestion.champs import FactureEntree, FluxPrevuEntree, PaiementEntree

M = TypeVar("M", bound=BaseModel)
_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkg": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def _colonne_index(reference: str) -> int:
    """Convertit A, B... AA en indice de colonne zero-base."""
    lettres = re.match(r"[A-Z]+", reference.upper())
    if lettres is None:
        raise ValueError(f"Reference de cellule Excel invalide : {reference}")
    valeur = 0
    for lettre in lettres.group(0):
        valeur = valeur * 26 + ord(lettre) - ord("A") + 1
    return valeur - 1


def _lire_xlsx(chemin: Path, feuille: str | None = None) -> pd.DataFrame:
    """Lit les cellules d'une feuille XLSX avec zipfile et XML standard."""
    with ZipFile(chemin) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        cibles = {
            relation.attrib["Id"]: relation.attrib["Target"]
            for relation in relations.findall("pkg:Relationship", _NS)
        }
        feuilles = workbook.findall("main:sheets/main:sheet", _NS)
        if not feuilles:
            raise ValueError("Le classeur Excel ne contient aucune feuille.")
        choisie = next((f for f in feuilles if f.attrib["name"] == feuille), None) if feuille else feuilles[0]
        if choisie is None:
            raise ValueError(f"Feuille Excel introuvable : {feuille}")
        cible = cibles[choisie.attrib[f"{{{_NS['rel']}}}id"]].lstrip("/")
        if not cible.startswith("xl/"):
            cible = f"xl/{cible}"
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root_shared = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.itertext()) for node in root_shared.findall("main:si", _NS)]
        root = ET.fromstring(archive.read(cible))
        matrice: list[list[str]] = []
        for row in root.findall("main:sheetData/main:row", _NS):
            cellules: list[str] = []
            for cell in row.findall("main:c", _NS):
                index = _colonne_index(cell.attrib["r"])
                while len(cellules) <= index:
                    cellules.append("")
                value = cell.find("main:v", _NS)
                if cell.attrib.get("t") == "inlineStr":
                    texte = "".join(cell.find("main:is", _NS).itertext())  # type: ignore[union-attr]
                elif value is None or value.text is None:
                    texte = ""
                elif cell.attrib.get("t") == "s":
                    texte = shared[int(value.text)]
                else:
                    texte = value.text
                cellules[index] = texte
            matrice.append(cellules)
    if not matrice:
        return pd.DataFrame()
    entetes = matrice[0]
    return pd.DataFrame(
        [dict(zip(entetes, row)) for row in matrice[1:] if any(row)],
        columns=entetes,
    )


def lire_tableau(chemin: str | Path, *, feuille: str | None = None) -> pd.DataFrame:
    """Lit un CSV ou un classeur XLSX en texte pour eviter les conversions flottantes."""
    fichier = Path(chemin)
    extension = fichier.suffix.lower()
    if extension == ".csv":
        return pd.read_csv(fichier, dtype=str, keep_default_na=False)
    if extension == ".xlsx":
        return _lire_xlsx(fichier, feuille)
    raise ValueError("Format non pris en charge. Utilisez un fichier CSV ou XLSX.")


def importer_factures(
    chemin: str | Path,
    mappage_colonnes: dict[str, str] | None = None,
    *,
    feuille: str | None = None,
) -> list[FactureEntree]:
    """Importe et valide des factures depuis CSV/XLSX avec alias de colonnes."""
    return importer_modeles(
        chemin, FactureEntree, mappage_colonnes, feuille=feuille
    )


def importer_paiements(
    chemin: str | Path,
    mappage_colonnes: dict[str, str] | None = None,
    *,
    feuille: str | None = None,
) -> list[PaiementEntree]:
    """Importe des paiements CSV/XLSX avec mappage de colonnes."""
    return importer_modeles(
        chemin, PaiementEntree, mappage_colonnes, feuille=feuille
    )


def importer_flux(
    chemin: str | Path,
    mappage_colonnes: dict[str, str] | None = None,
    *,
    feuille: str | None = None,
) -> list[FluxPrevuEntree]:
    """Importe des flux CSV/XLSX avec mappage de colonnes."""
    return importer_modeles(
        chemin, FluxPrevuEntree, mappage_colonnes, feuille=feuille
    )


def importer_modeles(
    chemin: str | Path,
    modele: type[M],
    mappage_colonnes: dict[str, str] | None = None,
    *,
    feuille: str | None = None,
) -> list[M]:
    """Importe un modele Pydantic depuis un tableau avec alias configurables."""
    tableau = lire_tableau(chemin, feuille=feuille)
    mappage: dict[str, str] = mappage_colonnes or {}
    resultats: list[M] = []
    for ligne in tableau.to_dict(orient="records"):
        normalisee: dict[str, Any] = {
            champ: ligne[colonne]
            for champ in modele.model_fields
            if (colonne := mappage.get(champ, champ)) in ligne
        }
        resultats.append(modele.model_validate(normalisee))
    return resultats
