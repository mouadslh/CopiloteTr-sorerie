"""Import local d'une facture UBL XML avec lxml securise."""

from __future__ import annotations

import re
from pathlib import Path

from lxml import etree

from app.ingestion.champs import FactureEntree

_NS = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}


def _texte(element: etree._Element, chemin: str, *, requis: bool = True) -> str | None:
    """Lit un texte UBL par XPath simplifie."""
    noeud = element.find(chemin, namespaces=_NS)
    if noeud is None or noeud.text is None:
        if requis:
            raise ValueError(f"Champ UBL requis manquant : {chemin}")
        return None
    return noeud.text.strip()


def importer_ubl(chemin: str | Path) -> FactureEntree:
    """Transforme une facture UBL en modele valide, sans resolution reseau."""
    parseur = etree.XMLParser(resolve_entities=False, no_network=True, recover=False)
    racine = etree.parse(str(chemin), parseur).getroot()
    numero = _texte(racine, "cbc:ID")
    date_facture = _texte(racine, "cbc:IssueDate")
    ice = _texte(racine, "cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID")
    nom = _texte(racine, "cac:AccountingCustomerParty/cac:Party/cac:PartyName/cbc:Name")
    ht = _texte(racine, "cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount")
    ttc = _texte(racine, "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount")
    tva = _texte(racine, "cac:TaxTotal/cbc:TaxAmount")
    delai_text = _texte(racine, "cac:PaymentTerms/cbc:Note", requis=False)
    delai_match = re.search(r"\d+", delai_text or "")
    return FactureEntree.model_validate(
        {
            "numero": numero,
            "client_nom": nom,
            "client_ice": ice,
            "date_facture": date_facture,
            "montant_ht": ht,
            "montant_tva": tva,
            "montant_ttc": ttc,
            "delai_conventionnel_jours": int(delai_match.group()) if delai_match else None,
            "statut": "impayee",
        }
    )
