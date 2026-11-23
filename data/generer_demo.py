"""Genere les donnees fictives Atlas de maniere reproductible."""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

DOSSIER = Path(__file__).with_name("demo")
GRAINE = 69
CLIENTS = {
    "A": {"nom": "Promoteur Atlas", "ice": "001234567890123", "secteur": "promotion immobiliere", "delai": 90, "retards": [32, 33, 35, 35, 37], "ht": 150000},
    "B": {"nom": "Hotel Atlas", "ice": "002345678901234", "secteur": "hotellerie", "delai": "", "retards": [17, 18, 20, 20, 23], "ht": 50000},
    "C": {"nom": "Grossiste Atlas", "ice": "003456789012345", "secteur": "commerce de gros", "delai": 60, "retards": [7, 8, 10, 10, 13], "ht": 100000},
}
CHAMPS_FACTURE = [
    "numero", "client_nom", "client_ice", "secteur", "date_facture", "montant_ht",
    "montant_tva", "montant_ttc", "delai_conventionnel_jours", "statut",
]


def _ecrire_csv(chemin: Path, champs: list[str], lignes: list[dict[str, object]]) -> None:
    """Ecrit un CSV UTF-8 stable, sans index ni conversion flottante."""
    with chemin.open("w", encoding="utf-8", newline="") as flux:
        writer = csv.DictWriter(flux, fieldnames=champs, lineterminator="\n")
        writer.writeheader()
        writer.writerows(lignes)


def generer(dossier: str | Path = DOSSIER) -> None:
    """Produit les factures, paiements, flux et exemples bruités/UBL."""
    destination = Path(dossier)
    destination.mkdir(parents=True, exist_ok=True)
    rng = random.Random(GRAINE)
    factures: list[dict[str, object]] = []
    paiements: list[dict[str, object]] = []
    for code, client in CLIENTS.items():
        delai = int(client["delai"] or 60)
        for index, retard in enumerate(client["retards"], start=1):
            ht = int(client["ht"]) + rng.randrange(0, 11) * 100
            date_facture = date(2026, index, 5) + timedelta(days=ord(code) - ord("A"))
            numero = f"AT-{code}-H{index:02d}"
            tva = Decimal(ht) * Decimal("0.20")
            factures.append(
                {
                    "numero": numero,
                    "client_nom": client["nom"],
                    "client_ice": client["ice"],
                    "secteur": client["secteur"],
                    "date_facture": date_facture.isoformat(),
                    "montant_ht": str(Decimal(ht).quantize(Decimal("0.01"))),
                    "montant_tva": str(tva.quantize(Decimal("0.01"))),
                    "montant_ttc": str((Decimal(ht) + tva).quantize(Decimal("0.01"))),
                    "delai_conventionnel_jours": client["delai"],
                    "statut": "payee",
                }
            )
            date_paiement = date_facture + timedelta(days=delai + int(retard))
            paiements.append(
                {
                    "numero_facture": numero,
                    "date_paiement": date_paiement.isoformat(),
                    "montant": factures[-1]["montant_ttc"],
                }
            )
    factures.extend(
        [
            {
                "numero": "AT-A-2026-08", "client_nom": CLIENTS["A"]["nom"],
                "client_ice": CLIENTS["A"]["ice"], "secteur": CLIENTS["A"]["secteur"],
                "date_facture": "2026-08-15", "montant_ht": "150000.00", "montant_tva": "30000.00",
                "montant_ttc": "180000.00", "delai_conventionnel_jours": 90, "statut": "impayee",
            },
            {
                "numero": "AT-B-2026-09", "client_nom": CLIENTS["B"]["nom"],
                "client_ice": CLIENTS["B"]["ice"], "secteur": CLIENTS["B"]["secteur"],
                "date_facture": "2026-09-01", "montant_ht": "50000.00", "montant_tva": "10000.00",
                "montant_ttc": "60000.00", "delai_conventionnel_jours": "", "statut": "impayee",
            },
            {
                "numero": "AT-C-2026-10", "client_nom": CLIENTS["C"]["nom"],
                "client_ice": CLIENTS["C"]["ice"], "secteur": CLIENTS["C"]["secteur"],
                "date_facture": "2026-10-01", "montant_ht": "100000.00", "montant_tva": "20000.00",
                "montant_ttc": "120000.00", "delai_conventionnel_jours": 150, "statut": "impayee",
            },
        ]
    )
    _ecrire_csv(destination / "factures.csv", CHAMPS_FACTURE, factures)
    _ecrire_csv(
        destination / "paiements.csv",
        ["numero_facture", "date_paiement", "montant"],
        paiements,
    )
    _ecrire_csv(
        destination / "flux_prevus.csv",
        ["libelle", "date_flux", "montant"],
        [
            {"libelle": "Fournisseur de bois", "date_flux": "2026-11-20", "montant": "-70000.00"},
            {"libelle": "Salaires", "date_flux": "2026-11-30", "montant": "-55000.00"},
        ],
    )
    bruitees = [dict(factures[-3]), dict(factures[-2])]
    bruitees[0]["numero"] = "AT-BRUIT-HT-TVA"
    bruitees[0]["montant_ttc"] = "59999.00"
    bruitees[1]["numero"] = "AT-BRUIT-ICE"
    bruitees[1]["client_ice"] = "ICE-INVALIDE"
    _ecrire_csv(destination / "factures_bruitees.csv", CHAMPS_FACTURE, bruitees)
    (destination / "exemple_ubl.xml").write_text(_ubl_exemple(), encoding="utf-8")


def _ubl_exemple() -> str:
    """Construit une facture UBL fictive de demonstration."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:ID>UBL-AT-001</cbc:ID><cbc:IssueDate>2026-11-01</cbc:IssueDate>
  <cac:AccountingCustomerParty><cac:Party>
    <cac:PartyName><cbc:Name>Client UBL Fictif</cbc:Name></cac:PartyName>
    <cac:PartyTaxScheme><cbc:CompanyID>004567890123456</cbc:CompanyID></cac:PartyTaxScheme>
  </cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount currencyID="MAD">200.00</cbc:TaxAmount></cac:TaxTotal>
  <cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount currencyID="MAD">1000.00</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount currencyID="MAD">1200.00</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
  <cac:PaymentTerms><cbc:Note>Delai contractuel 45 jours</cbc:Note></cac:PaymentTerms>
</Invoice>
'''


if __name__ == "__main__":
    generer()
