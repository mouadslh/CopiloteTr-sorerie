PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS entreprise (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    ville TEXT NOT NULL,
    date_reference TEXT NOT NULL,
    solde_initial TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS client (
    ice TEXT PRIMARY KEY CHECK (length(ice) = 15 AND ice NOT GLOB '*[^0-9]*'),
    nom TEXT NOT NULL,
    secteur TEXT NOT NULL DEFAULT 'inconnu'
);

CREATE TABLE IF NOT EXISTS facture (
    numero TEXT PRIMARY KEY,
    client_ice TEXT NOT NULL REFERENCES client(ice),
    date_facture TEXT NOT NULL,
    montant_ht TEXT NOT NULL,
    montant_tva TEXT NOT NULL,
    montant_ttc TEXT NOT NULL,
    delai_conventionnel_jours INTEGER CHECK (delai_conventionnel_jours IS NULL OR delai_conventionnel_jours >= 0),
    statut TEXT NOT NULL CHECK (statut IN ('impayee', 'payee', 'partiellement_payee')),
    cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS paiement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facture_numero TEXT NOT NULL REFERENCES facture(numero),
    date_paiement TEXT NOT NULL,
    montant TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flux_prevu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle TEXT NOT NULL,
    date_flux TEXT NOT NULL,
    montant TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS parametre_legal (
    effet_a_partir_du TEXT PRIMARY KEY,
    delai_defaut_jours INTEGER NOT NULL,
    plafond_conventionnel_jours INTEGER NOT NULL,
    plafond_sectoriel_jours INTEGER NOT NULL,
    taux_directeur TEXT NOT NULL,
    majoration_par_mois_sup TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS action (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facture_numero TEXT REFERENCES facture(numero),
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_objet TEXT NOT NULL,
    identifiant_objet TEXT NOT NULL,
    operation TEXT NOT NULL,
    date_operation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT NOT NULL DEFAULT '{}'
);
