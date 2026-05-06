"""
scripts/enrich_sovereignty.py

Combineert domein-, leverancier- en netwerkdata tot een soevereiniteitsanalyse.

Input:
- data/processed/latest/domains_network_enriched.csv
- data/processed/latest/supplier_indicators.csv
- data/lookups/sovereignty_catalog.csv, wordt automatisch aangemaakt als deze ontbreekt

Output:
- data/processed/latest/dataflow_matrix.csv
- data/processed/latest/sovereignty_summary.csv
- data/processed/latest/verification_questions.csv

Gebruik:
    python scripts/enrich_sovereignty.py \
      --domains data/processed/latest/domains_network_enriched.csv \
      --suppliers data/processed/latest/supplier_indicators.csv \
      --catalog data/lookups/sovereignty_catalog.csv \
      --output-dir data/processed/latest

Doel:
- Niet bewijzen waar data juridisch of fysiek staat
- Wel zichtbaar maken welke publieke indicatoren wijzen op cloud-, mail-, CDN-, analytics- of SaaS-afhankelijkheden
- Expliciet aangeven wat publiek niet vast te stellen is en dus verificatie vraagt
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd


DEFAULT_CATALOG_ROWS = [
    {
        "indicator": "protection.outlook.com",
        "supplier_name": "Microsoft 365 / Exchange Online",
        "supplier_type": "mail/cloud",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier, EU region possible",
        "data_risk": "high",
        "typical_data": "email content, email metadata, account identifiers",
        "verification_question": "Welke Microsoft 365 tenantregio, workloads, logginglocaties, supporttoegang en subverwerkers zijn van toepassing?",
        "source_layer": "mx_spf",
    },
    {
        "indicator": "outlook.com",
        "supplier_name": "Microsoft 365 / Exchange Online",
        "supplier_type": "mail/cloud",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier, EU region possible",
        "data_risk": "high",
        "typical_data": "email content, email metadata, account identifiers",
        "verification_question": "Welke Microsoft 365 tenantregio, workloads, logginglocaties, supporttoegang en subverwerkers zijn van toepassing?",
        "source_layer": "mx_spf",
    },
    {
        "indicator": "azure",
        "supplier_name": "Microsoft Azure",
        "supplier_type": "cloud hosting / platform",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier, EU region possible",
        "data_risk": "medium/high",
        "typical_data": "application data, logs, telemetry, backups possible",
        "verification_question": "Welke Azure-regio's, tenants, logginglocaties en subverwerkers worden gebruikt?",
        "source_layer": "network_hosting",
    },
    {
        "indicator": "googleapis.com",
        "supplier_name": "Google APIs",
        "supplier_type": "frontend / API / SaaS",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier",
        "data_risk": "medium",
        "typical_data": "browser metadata, IP address, request metadata, usage data possible",
        "verification_question": "Welke Google-diensten worden geladen, met welk doel, en is lokaal hosten of Europese alternatieven mogelijk?",
        "source_layer": "frontend_scripts",
    },
    {
        "indicator": "googletagmanager.com",
        "supplier_name": "Google Tag Manager",
        "supplier_type": "tag management / analytics enabler",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier",
        "data_risk": "high",
        "typical_data": "browser metadata, event data, tags loaded by configuration",
        "verification_question": "Welke tags zijn actief binnen Google Tag Manager en welke persoonsgegevens of identifiers worden verwerkt?",
        "source_layer": "frontend_scripts",
    },
    {
        "indicator": "google-analytics.com",
        "supplier_name": "Google Analytics",
        "supplier_type": "analytics",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier",
        "data_risk": "high",
        "typical_data": "analytics identifiers, browser metadata, usage data",
        "verification_question": "Wordt Google Analytics gebruikt, hoe is IP-anonimisering ingericht, en welke doorgiftewaarborgen bestaan?",
        "source_layer": "frontend_scripts",
    },
    {
        "indicator": "youtube.com",
        "supplier_name": "YouTube",
        "supplier_type": "embedded media",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier",
        "data_risk": "medium/high",
        "typical_data": "browser metadata, viewing data, cookies possible",
        "verification_question": "Worden YouTube embeds privacyvriendelijk geladen en is toestemming of een alternatief ingericht?",
        "source_layer": "frontend_scripts",
    },
    {
        "indicator": "cloudflare",
        "supplier_name": "Cloudflare",
        "supplier_type": "CDN/WAF/DNS",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier, global edge",
        "data_risk": "medium/high",
        "typical_data": "IP address, headers, request metadata, security logs",
        "verification_question": "Welke Cloudflare-diensten worden gebruikt, waar worden logs verwerkt en welke dataverwerkingsafspraken gelden?",
        "source_layer": "network_hosting",
    },
    {
        "indicator": "akamai",
        "supplier_name": "Akamai",
        "supplier_type": "CDN/WAF",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier, global edge",
        "data_risk": "medium/high",
        "typical_data": "IP address, headers, request metadata, security logs",
        "verification_question": "Welke Akamai-diensten worden gebruikt en waar worden requestlogs verwerkt?",
        "source_layer": "network_hosting",
    },
    {
        "indicator": "amazonaws.com",
        "supplier_name": "Amazon Web Services",
        "supplier_type": "cloud hosting / email / storage",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier, region depends on configuration",
        "data_risk": "medium/high",
        "typical_data": "application data, logs, email, storage possible",
        "verification_question": "Welke AWS-regio's en diensten worden gebruikt en welke data, logs en back-ups staan daar?",
        "source_layer": "network_hosting",
    },
    {
        "indicator": "cloudfront",
        "supplier_name": "Amazon CloudFront",
        "supplier_type": "CDN",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier, global edge",
        "data_risk": "medium",
        "typical_data": "IP address, headers, request metadata, CDN logs",
        "verification_question": "Welke data en logs lopen via CloudFront en waar worden die verwerkt?",
        "source_layer": "network_hosting",
    },
    {
        "indicator": "sendgrid.net",
        "supplier_name": "SendGrid",
        "supplier_type": "transactional email",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier",
        "data_risk": "medium/high",
        "typical_data": "email content, recipient metadata, delivery logs",
        "verification_question": "Welke mailstromen lopen via SendGrid en welke bewaartermijnen en subverwerkers gelden?",
        "source_layer": "mx_spf",
    },
    {
        "indicator": "mailgun.org",
        "supplier_name": "Mailgun",
        "supplier_type": "transactional email",
        "parent_company_country": "US",
        "jurisdiction_group": "US supplier",
        "data_risk": "medium/high",
        "typical_data": "email content, recipient metadata, delivery logs",
        "verification_question": "Welke mailstromen lopen via Mailgun en welke bewaartermijnen en subverwerkers gelden?",
        "source_layer": "mx_spf",
    },
    {
        "indicator": "zivver.com",
        "supplier_name": "Zivver",
        "supplier_type": "secure email",
        "parent_company_country": "NL",
        "jurisdiction_group": "NL/EU supplier",
        "data_risk": "medium/high",
        "typical_data": "secure email content, recipient metadata, access logs",
        "verification_question": "Welke berichtenstromen lopen via Zivver en welke subverwerkers en hostinglocaties worden gebruikt?",
        "source_layer": "mx_spf",
    },
    {
        "indicator": "topdesk.net",
        "supplier_name": "TOPdesk",
        "supplier_type": "service management / SaaS",
        "parent_company_country": "NL",
        "jurisdiction_group": "NL/EU supplier",
        "data_risk": "medium/high",
        "typical_data": "tickets, contact details, internal service data",
        "verification_question": "Welke TOPdesk-omgeving wordt gebruikt, waar staat deze gehost en welke subverwerkers gelden?",
        "source_layer": "mx_spf",
    },
    {
        "indicator": "flowmailer.net",
        "supplier_name": "Flowmailer",
        "supplier_type": "transactional email",
        "parent_company_country": "NL",
        "jurisdiction_group": "NL/EU supplier",
        "data_risk": "medium/high",
        "typical_data": "email content, recipient metadata, delivery logs",
        "verification_question": "Welke mailstromen lopen via Flowmailer en waar worden inhoud, metadata en logs verwerkt?",
        "source_layer": "mx_spf",
    },
    {
        "indicator": "formulierenserver.nl",
        "supplier_name": "Formulierenserver",
        "supplier_type": "forms / e-government SaaS",
        "parent_company_country": "NL",
        "jurisdiction_group": "NL/EU supplier",
        "data_risk": "high",
        "typical_data": "form submissions, contact details, potentially sensitive citizen data",
        "verification_question": "Welke formulieren lopen via Formulierenserver, waar worden inzendingen, bijlagen en logs opgeslagen?",
        "source_layer": "mx_spf",
    },
    {
        "indicator": "simgroep",
        "supplier_name": "SIMgroep",
        "supplier_type": "municipal website / CMS / CDN",
        "parent_company_country": "NL",
        "jurisdiction_group": "NL/EU supplier",
        "data_risk": "medium/high",
        "typical_data": "website content, forms, usage logs, citizen interactions possible",
        "verification_question": "Welke SIMgroep-diensten worden gebruikt en welke hosting, CDN, logging en subverwerkers zijn van toepassing?",
        "source_layer": "network_hosting",
    },
    {
        "indicator": "siteimprove",
        "supplier_name": "Siteimprove",
        "supplier_type": "analytics / accessibility / quality monitoring",
        "parent_company_country": "DK/US presence",
        "jurisdiction_group": "EU supplier with international presence",
        "data_risk": "medium",
        "typical_data": "website usage, quality metrics, browser metadata possible",
        "verification_question": "Welke Siteimprove-modules zijn actief en worden persoonsgegevens of identifiers verwerkt?",
        "source_layer": "frontend_scripts",
    },
    {
        "indicator": "readspeaker",
        "supplier_name": "ReadSpeaker",
        "supplier_type": "accessibility / text-to-speech",
        "parent_company_country": "NL/International",
        "jurisdiction_group": "EU supplier with international presence",
        "data_risk": "low/medium",
        "typical_data": "requested page text, IP address, browser metadata possible",
        "verification_question": "Welke gegevens worden door ReadSpeaker verwerkt en waar worden logs opgeslagen?",
        "source_layer": "frontend_scripts",
    },
    {
        "indicator": "cookiefirst",
        "supplier_name": "CookieFirst",
        "supplier_type": "cookie consent management",
        "parent_company_country": "NL",
        "jurisdiction_group": "NL/EU supplier",
        "data_risk": "low/medium",
        "typical_data": "consent preferences, browser metadata possible",
        "verification_question": "Welke consentgegevens worden opgeslagen en waar?",
        "source_layer": "frontend_scripts",
    },
    {
        "indicator": "cookiebot",
        "supplier_name": "Cookiebot / Usercentrics",
        "supplier_type": "cookie consent management",
        "parent_company_country": "DE/DK",
        "jurisdiction_group": "EU supplier",
        "data_risk": "low/medium",
        "typical_data": "consent preferences, browser metadata possible",
        "verification_question": "Welke consentgegevens worden opgeslagen, waar en met welke subverwerkers?",
        "source_layer": "frontend_scripts",
    },
]


@dataclass
class DataflowRow:
    domain: str
    service_layer: str
    supplier: str
    supplier_type: str
    indicator: str
    evidence_source: str
    evidence_value: str
    jurisdiction_group: str
    parent_company_country: str
    data_risk: str
    typical_data: str
    personal_data_likelihood: str
    public_service_layer: str
    confidence: str
    verification_needed: str
    verification_question: str


def ensure_catalog(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(DEFAULT_CATALOG_ROWS)
    df.to_csv(path, index=False)
    return df


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    if text.lower() == "nan":
        return ""
    return text.strip()


def split_indicators(value: object) -> List[str]:
    text = clean_text(value)
    if not text:
        return []
    parts = re.split(r"[,;|\n\t ]+", text)
    return [p.strip().lower() for p in parts if p.strip()]


def boolish(value: object) -> bool:
    text = clean_text(value).lower()
    return text in {"true", "1", "yes", "ja", "y"}


def infer_confidence(evidence_source: str, evidence_value: str, catalog_indicator: str) -> str:
    if catalog_indicator in evidence_value.lower():
        return "hoog"
    if evidence_source in {"hosting_hint", "network_provider_hint", "cloud_or_cdn_hint", "mail_provider_hint"}:
        return "middel"
    return "laag"


def infer_service_layer(evidence_source: str, catalog_source_layer: str) -> str:
    if catalog_source_layer:
        return catalog_source_layer
    if evidence_source in {"mx", "spf", "spf_includes", "mail_provider_hint", "mail_sovereignty_hint"}:
        return "mx_spf"
    if evidence_source in {"external_script_domains", "tracker_hints"}:
        return "frontend_scripts"
    if evidence_source in {"hosting_hint", "network_provider_hint", "cloud_or_cdn_hint", "network_jurisdiction_hint"}:
        return "network_hosting"
    return "unknown"


def evidence_fields(row: pd.Series) -> Dict[str, str]:
    candidates = [
        "mx",
        "spf",
        "spf_includes",
        "mx_providers",
        "mail_provider_hint",
        "mail_sovereignty_hint",
        "external_script_domains",
        "tracker_hints",
        "hosting_hint",
        "sovereignty_hint",
        "network_provider_hint",
        "cloud_or_cdn_hint",
        "network_jurisdiction_hint",
        "server_header",
        "cname",
        "nameservers",
    ]
    return {field: clean_text(row.get(field, "")) for field in candidates if clean_text(row.get(field, ""))}


def match_catalog(domain_row: pd.Series, catalog: pd.DataFrame) -> List[DataflowRow]:
    domain = clean_text(domain_row.get("domain", ""))
    public_service_layer = clean_text(domain_row.get("layer", "Onbekend"))
    personal_data_likelihood = clean_text(domain_row.get("personal_data_likelihood", "Te beoordelen"))
    evidence = evidence_fields(domain_row)
    matches: List[DataflowRow] = []

    for _, cat in catalog.iterrows():
        indicator = clean_text(cat.get("indicator", "")).lower()
        if not indicator:
            continue

        for source, value in evidence.items():
            if indicator in value.lower():
                service_layer = infer_service_layer(source, clean_text(cat.get("source_layer", "")))
                confidence = infer_confidence(source, value, indicator)
                verification_question = clean_text(cat.get("verification_question", ""))
                matches.append(
                    DataflowRow(
                        domain=domain,
                        service_layer=service_layer,
                        supplier=clean_text(cat.get("supplier_name", "")),
                        supplier_type=clean_text(cat.get("supplier_type", "")),
                        indicator=indicator,
                        evidence_source=source,
                        evidence_value=value[:500],
                        jurisdiction_group=clean_text(cat.get("jurisdiction_group", "")),
                        parent_company_country=clean_text(cat.get("parent_company_country", "")),
                        data_risk=clean_text(cat.get("data_risk", "")),
                        typical_data=clean_text(cat.get("typical_data", "")),
                        personal_data_likelihood=personal_data_likelihood,
                        public_service_layer=public_service_layer,
                        confidence=confidence,
                        verification_needed="ja",
                        verification_question=verification_question,
                    )
                )

    # De-duplicate similar rows while preserving evidence richness.
    unique: Dict[tuple, DataflowRow] = {}
    for item in matches:
        key = (item.domain, item.service_layer, item.supplier, item.evidence_source, item.indicator)
        if key not in unique:
            unique[key] = item
    return list(unique.values())


def load_supplier_indicators(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def from_supplier_indicators(suppliers: pd.DataFrame, catalog: pd.DataFrame, domains: pd.DataFrame) -> List[DataflowRow]:
    if suppliers.empty:
        return []

    domain_lookup = domains.set_index("domain").to_dict(orient="index") if "domain" in domains.columns else {}
    rows: List[DataflowRow] = []

    text_columns = [c for c in suppliers.columns if c not in {"domain"}]
    for _, supplier_row in suppliers.iterrows():
        domain = clean_text(supplier_row.get("domain", ""))
        domain_meta = domain_lookup.get(domain, {})
        public_service_layer = clean_text(domain_meta.get("layer", "Onbekend"))
        personal_data_likelihood = clean_text(domain_meta.get("personal_data_likelihood", "Te beoordelen"))

        for col in text_columns:
            value = clean_text(supplier_row.get(col, ""))
            if not value:
                continue
            for _, cat in catalog.iterrows():
                indicator = clean_text(cat.get("indicator", "")).lower()
                if indicator and indicator in value.lower():
                    rows.append(
                        DataflowRow(
                            domain=domain,
                            service_layer=infer_service_layer(col, clean_text(cat.get("source_layer", ""))),
                            supplier=clean_text(cat.get("supplier_name", "")),
                            supplier_type=clean_text(cat.get("supplier_type", "")),
                            indicator=indicator,
                            evidence_source=f"supplier_indicators.{col}",
                            evidence_value=value[:500],
                            jurisdiction_group=clean_text(cat.get("jurisdiction_group", "")),
                            parent_company_country=clean_text(cat.get("parent_company_country", "")),
                            data_risk=clean_text(cat.get("data_risk", "")),
                            typical_data=clean_text(cat.get("typical_data", "")),
                            personal_data_likelihood=personal_data_likelihood,
                            public_service_layer=public_service_layer,
                            confidence="hoog",
                            verification_needed="ja",
                            verification_question=clean_text(cat.get("verification_question", "")),
                        )
                    )

    unique: Dict[tuple, DataflowRow] = {}
    for item in rows:
        key = (item.domain, item.service_layer, item.supplier, item.evidence_source, item.indicator)
        if key not in unique:
            unique[key] = item
    return list(unique.values())


def make_summary(domains: pd.DataFrame, matrix: pd.DataFrame) -> pd.DataFrame:
    def contains(series: pd.Series, needle: str) -> int:
        if series.empty:
            return 0
        return int(series.fillna("").astype(str).str.contains(needle, case=False, regex=False).sum())

    domains_total = len(domains)
    suppliers_total = matrix["supplier"].nunique() if not matrix.empty else 0
    dataflows_total = len(matrix)
    us_supplier_domains = matrix.loc[
        matrix["jurisdiction_group"].fillna("").str.contains("US", case=False, regex=False), "domain"
    ].nunique() if not matrix.empty else 0
    nl_eu_supplier_domains = matrix.loc[
        matrix["jurisdiction_group"].fillna("").str.contains("NL", case=False, regex=False)
        | matrix["jurisdiction_group"].fillna("").str.contains("EU", case=False, regex=False), "domain"
    ].nunique() if not matrix.empty else 0
    high_data_risk_domains = matrix.loc[
        matrix["data_risk"].fillna("").str.contains("high", case=False, regex=False), "domain"
    ].nunique() if not matrix.empty else 0
    unknown_network_domains = contains(domains.get("network_jurisdiction_hint", pd.Series(dtype=str)), "Onbekend")

    rows = [
        {"metric": "domains_total", "value": domains_total},
        {"metric": "dataflow_indicators_total", "value": dataflows_total},
        {"metric": "unique_suppliers_detected", "value": suppliers_total},
        {"metric": "domains_with_us_supplier_indicator", "value": us_supplier_domains},
        {"metric": "domains_with_nl_or_eu_supplier_indicator", "value": nl_eu_supplier_domains},
        {"metric": "domains_with_high_data_risk_indicator", "value": high_data_risk_domains},
        {"metric": "domains_with_unknown_network_jurisdiction", "value": unknown_network_domains},
    ]
    return pd.DataFrame(rows)


def make_verification_questions(matrix: pd.DataFrame) -> pd.DataFrame:
    if matrix.empty:
        return pd.DataFrame(columns=["priority", "domain", "supplier", "service_layer", "question", "reason"])

    rows = []
    for _, item in matrix.iterrows():
        risk = clean_text(item.get("data_risk", "")).lower()
        jurisdiction = clean_text(item.get("jurisdiction_group", ""))
        personal = clean_text(item.get("personal_data_likelihood", ""))
        priority = "P3"
        if "high" in risk and "US" in jurisdiction:
            priority = "P1"
        elif "high" in risk or "US" in jurisdiction:
            priority = "P2"

        reason_parts = []
        if jurisdiction:
            reason_parts.append(f"jurisdictie: {jurisdiction}")
        if risk:
            reason_parts.append(f"datarisico: {risk}")
        if personal:
            reason_parts.append(f"persoonsgegevens: {personal}")

        rows.append(
            {
                "priority": priority,
                "domain": clean_text(item.get("domain", "")),
                "supplier": clean_text(item.get("supplier", "")),
                "service_layer": clean_text(item.get("service_layer", "")),
                "question": clean_text(item.get("verification_question", "")),
                "reason": "; ".join(reason_parts),
            }
        )

    df = pd.DataFrame(rows).drop_duplicates()
    priority_order = {"P1": 1, "P2": 2, "P3": 3}
    df["_priority_order"] = df["priority"].map(priority_order).fillna(9)
    df = df.sort_values(["_priority_order", "domain", "supplier"]).drop(columns=["_priority_order"])
    return df


def enrich(domains_path: Path, suppliers_path: Path, catalog_path: Path, output_dir: Path) -> None:
    domains = pd.read_csv(domains_path)
    suppliers = load_supplier_indicators(suppliers_path)
    catalog = ensure_catalog(catalog_path)

    matrix_rows: List[DataflowRow] = []
    for _, row in domains.iterrows():
        matrix_rows.extend(match_catalog(row, catalog))
    matrix_rows.extend(from_supplier_indicators(suppliers, catalog, domains))

    unique: Dict[tuple, DataflowRow] = {}
    for item in matrix_rows:
        key = (item.domain, item.service_layer, item.supplier, item.evidence_source, item.indicator)
        if key not in unique:
            unique[key] = item

    matrix = pd.DataFrame([asdict(row) for row in unique.values()])
    if matrix.empty:
        matrix = pd.DataFrame(columns=[field for field in DataflowRow.__dataclass_fields__.keys()])

    summary = make_summary(domains, matrix)
    questions = make_verification_questions(matrix)

    output_dir.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(output_dir / "dataflow_matrix.csv", index=False)
    summary.to_csv(output_dir / "sovereignty_summary.csv", index=False)
    questions.to_csv(output_dir / "verification_questions.csv", index=False)

    print(f"[OK] wrote {output_dir / 'dataflow_matrix.csv'} with {len(matrix)} rows")
    print(f"[OK] wrote {output_dir / 'sovereignty_summary.csv'}")
    print(f"[OK] wrote {output_dir / 'verification_questions.csv'} with {len(questions)} rows")


def main() -> None:
    parser = argparse.ArgumentParser(description="Maak soevereiniteitsanalyse op basis van publieke domeinindicatoren")
    parser.add_argument("--domains", default="data/processed/latest/domains_network_enriched.csv")
    parser.add_argument("--suppliers", default="data/processed/latest/supplier_indicators.csv")
    parser.add_argument("--catalog", default="data/lookups/sovereignty_catalog.csv")
    parser.add_argument("--output-dir", default="data/processed/latest")
    args = parser.parse_args()

    enrich(Path(args.domains), Path(args.suppliers), Path(args.catalog), Path(args.output_dir))


if __name__ == "__main__":
    main()
