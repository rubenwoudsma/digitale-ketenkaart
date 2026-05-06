"""
scripts/summarize_sovereignty.py

Maakt compacte analysebestanden op basis van dataflow_matrix.csv,
verification_questions.csv en domains_network_enriched.csv.

Input:
- data/processed/latest/dataflow_matrix.csv
- data/processed/latest/verification_questions.csv
- data/processed/latest/domains_network_enriched.csv

Output:
- data/processed/latest/supplier_summary.csv
- data/processed/latest/domain_priority_summary.csv
- data/processed/latest/service_layer_summary.csv
- data/processed/latest/key_findings.csv

Gebruik:
    python scripts/summarize_sovereignty.py \
      --processed-dir data/processed/latest
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import pandas as pd


PRIORITY_ORDER = {"P1": 1, "P2": 2, "P3": 3, "": 9}
RISK_ORDER = {"high": 4, "medium/high": 3, "medium": 2, "low/medium": 1, "low": 0, "": -1}


def clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Bestand niet gevonden: {path}")
    return pd.read_csv(path)


def contains_us(value: object) -> bool:
    return "us" in clean(value).lower()


def contains_nl_or_eu(value: object) -> bool:
    text = clean(value).lower()
    return "nl" in text or "eu" in text or "europe" in text


def normalize_risk(value: object) -> str:
    text = clean(value).lower()
    if "high" in text and "medium" in text:
        return "medium/high"
    if "high" in text:
        return "high"
    if "medium" in text and "low" in text:
        return "low/medium"
    if "medium" in text:
        return "medium"
    if "low" in text:
        return "low"
    return ""


def highest_risk(values: pd.Series) -> str:
    risks = [normalize_risk(v) for v in values]
    if not risks:
        return ""
    return max(risks, key=lambda r: RISK_ORDER.get(r, -1))


def join_unique(values: pd.Series, limit: int = 8) -> str:
    unique = []
    for value in values.dropna().astype(str):
        value = value.strip()
        if value and value.lower() != "nan" and value not in unique:
            unique.append(value)
    if len(unique) > limit:
        return ", ".join(unique[:limit]) + f", +{len(unique) - limit} meer"
    return ", ".join(unique)


def summarize_suppliers(matrix: pd.DataFrame, questions: pd.DataFrame) -> pd.DataFrame:
    if matrix.empty:
        return pd.DataFrame()

    p1_by_supplier = pd.Series(dtype=int)
    p2_by_supplier = pd.Series(dtype=int)
    if not questions.empty and "supplier" in questions.columns:
        p1_by_supplier = questions[questions.get("priority", "") == "P1"].groupby("supplier").size()
        p2_by_supplier = questions[questions.get("priority", "") == "P2"].groupby("supplier").size()

    rows: List[Dict[str, object]] = []
    for supplier, group in matrix.groupby("supplier", dropna=False):
        supplier = clean(supplier)
        jurisdictions = group.get("jurisdiction_group", pd.Series(dtype=str))
        service_layers = group.get("service_layer", pd.Series(dtype=str))
        data_risks = group.get("data_risk", pd.Series(dtype=str))
        domains = group.get("domain", pd.Series(dtype=str))

        rows.append(
            {
                "supplier": supplier,
                "supplier_type": join_unique(group.get("supplier_type", pd.Series(dtype=str)), limit=4),
                "jurisdiction_groups": join_unique(jurisdictions, limit=4),
                "parent_company_countries": join_unique(group.get("parent_company_country", pd.Series(dtype=str)), limit=4),
                "domains_count": domains.nunique(),
                "indicator_count": len(group),
                "service_layers": join_unique(service_layers, limit=6),
                "highest_data_risk": highest_risk(data_risks),
                "us_supplier_indicator": bool(jurisdictions.apply(contains_us).any()),
                "nl_or_eu_supplier_indicator": bool(jurisdictions.apply(contains_nl_or_eu).any()),
                "p1_questions_count": int(p1_by_supplier.get(supplier, 0)) if not p1_by_supplier.empty else 0,
                "p2_questions_count": int(p2_by_supplier.get(supplier, 0)) if not p2_by_supplier.empty else 0,
                "typical_data": join_unique(group.get("typical_data", pd.Series(dtype=str)), limit=5),
                "example_domains": join_unique(domains, limit=8),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    risk_rank = df["highest_data_risk"].map(RISK_ORDER).fillna(-1)
    df["_risk_rank"] = risk_rank
    df = df.sort_values(
        ["p1_questions_count", "domains_count", "_risk_rank", "indicator_count"],
        ascending=[False, False, False, False],
    ).drop(columns=["_risk_rank"])
    return df


def summarize_domains(matrix: pd.DataFrame, questions: pd.DataFrame, domains: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    domain_names = sorted(set(domains.get("domain", pd.Series(dtype=str)).dropna().astype(str)) | set(matrix.get("domain", pd.Series(dtype=str)).dropna().astype(str)))

    for domain in domain_names:
        m = matrix[matrix.get("domain", "") == domain] if not matrix.empty else pd.DataFrame()
        q = questions[questions.get("domain", "") == domain] if not questions.empty else pd.DataFrame()
        d = domains[domains.get("domain", "") == domain]
        drow = d.iloc[0].to_dict() if not d.empty else {}

        p1 = int((q.get("priority", pd.Series(dtype=str)) == "P1").sum()) if not q.empty else 0
        p2 = int((q.get("priority", pd.Series(dtype=str)) == "P2").sum()) if not q.empty else 0
        p3 = int((q.get("priority", pd.Series(dtype=str)) == "P3").sum()) if not q.empty else 0
        us_suppliers = m[m.get("jurisdiction_group", pd.Series(dtype=str)).apply(contains_us)] if not m.empty else pd.DataFrame()
        high_risk = m[m.get("data_risk", pd.Series(dtype=str)).apply(lambda x: "high" in clean(x).lower())] if not m.empty else pd.DataFrame()

        priority = "P3"
        reason_parts = []
        if p1 > 0:
            priority = "P1"
            reason_parts.append(f"{p1} P1-verificatievragen")
        elif p2 > 0:
            priority = "P2"
            reason_parts.append(f"{p2} P2-verificatievragen")

        personal_data = clean(drow.get("personal_data_likelihood", "")) or join_unique(m.get("personal_data_likelihood", pd.Series(dtype=str)), limit=2)
        public_layer = clean(drow.get("layer", "")) or join_unique(m.get("public_service_layer", pd.Series(dtype=str)), limit=2)
        network_jurisdiction = clean(drow.get("network_jurisdiction_hint", ""))

        if len(us_suppliers) > 0:
            reason_parts.append(f"{us_suppliers['supplier'].nunique()} leverancier(s) met US-indicatie")
        if len(high_risk) > 0:
            reason_parts.append(f"{high_risk['supplier'].nunique()} leverancier(s) met hoog datarisico")
        if "onbekend" in network_jurisdiction.lower():
            reason_parts.append("netwerkjurisdictie onbekend")

        rows.append(
            {
                "domain": domain,
                "priority": priority,
                "public_service_layer": public_layer,
                "personal_data_likelihood": personal_data,
                "network_provider_hint": clean(drow.get("network_provider_hint", "")),
                "cloud_or_cdn_hint": clean(drow.get("cloud_or_cdn_hint", "")),
                "network_jurisdiction_hint": network_jurisdiction,
                "unique_suppliers_count": m.get("supplier", pd.Series(dtype=str)).nunique() if not m.empty else 0,
                "us_supplier_count": us_suppliers.get("supplier", pd.Series(dtype=str)).nunique() if not us_suppliers.empty else 0,
                "high_risk_supplier_count": high_risk.get("supplier", pd.Series(dtype=str)).nunique() if not high_risk.empty else 0,
                "p1_questions_count": p1,
                "p2_questions_count": p2,
                "p3_questions_count": p3,
                "service_layers": join_unique(m.get("service_layer", pd.Series(dtype=str)), limit=5) if not m.empty else "",
                "example_suppliers": join_unique(m.get("supplier", pd.Series(dtype=str)), limit=8) if not m.empty else "",
                "priority_reason": "; ".join(reason_parts),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["_priority_order"] = df["priority"].map(PRIORITY_ORDER).fillna(9)
    df = df.sort_values(
        ["_priority_order", "p1_questions_count", "us_supplier_count", "high_risk_supplier_count"],
        ascending=[True, False, False, False],
    ).drop(columns=["_priority_order"])
    return df


def summarize_service_layers(matrix: pd.DataFrame) -> pd.DataFrame:
    if matrix.empty:
        return pd.DataFrame()

    rows = []
    for layer, group in matrix.groupby("service_layer", dropna=False):
        rows.append(
            {
                "service_layer": clean(layer),
                "domains_count": group.get("domain", pd.Series(dtype=str)).nunique(),
                "suppliers_count": group.get("supplier", pd.Series(dtype=str)).nunique(),
                "indicator_count": len(group),
                "us_supplier_domains_count": group[group.get("jurisdiction_group", pd.Series(dtype=str)).apply(contains_us)].get("domain", pd.Series(dtype=str)).nunique(),
                "high_data_risk_domains_count": group[group.get("data_risk", pd.Series(dtype=str)).apply(lambda x: "high" in clean(x).lower())].get("domain", pd.Series(dtype=str)).nunique(),
                "top_suppliers": join_unique(group.get("supplier", pd.Series(dtype=str)), limit=10),
            }
        )
    return pd.DataFrame(rows).sort_values("indicator_count", ascending=False)


def make_key_findings(matrix: pd.DataFrame, suppliers: pd.DataFrame, domains: pd.DataFrame, service_layers: pd.DataFrame, questions: pd.DataFrame) -> pd.DataFrame:
    findings = []

    findings.append({"finding": "onderzochte_domeinen", "value": int(domains.get("domain", pd.Series(dtype=str)).nunique())})
    findings.append({"finding": "datastroom_indicatoren", "value": int(len(matrix))})
    findings.append({"finding": "unieke_leveranciers", "value": int(matrix.get("supplier", pd.Series(dtype=str)).nunique() if not matrix.empty else 0)})
    findings.append({"finding": "domeinen_met_us_leveranciersindicatie", "value": int(domains[domains.get("us_supplier_count", 0) > 0]["domain"].nunique() if not domains.empty and "us_supplier_count" in domains.columns else 0)})
    findings.append({"finding": "p1_verificatievragen", "value": int((questions.get("priority", pd.Series(dtype=str)) == "P1").sum() if not questions.empty else 0)})
    findings.append({"finding": "p2_verificatievragen", "value": int((questions.get("priority", pd.Series(dtype=str)) == "P2").sum() if not questions.empty else 0)})

    if not suppliers.empty:
        top = suppliers.iloc[0]
        findings.append({"finding": "meest_prominente_leverancier", "value": clean(top.get("supplier", ""))})
        findings.append({"finding": "meest_prominente_leverancier_domeinen", "value": int(top.get("domains_count", 0))})

    if not service_layers.empty:
        top_layer = service_layers.iloc[0]
        findings.append({"finding": "grootste_service_layer", "value": clean(top_layer.get("service_layer", ""))})
        findings.append({"finding": "grootste_service_layer_indicatoren", "value": int(top_layer.get("indicator_count", 0))})

    return pd.DataFrame(findings)


def run(processed_dir: Path) -> None:
    matrix = read_csv(processed_dir / "dataflow_matrix.csv")
    questions = read_csv(processed_dir / "verification_questions.csv")
    domains_network = read_csv(processed_dir / "domains_network_enriched.csv")

    supplier_summary = summarize_suppliers(matrix, questions)
    domain_priority_summary = summarize_domains(matrix, questions, domains_network)
    service_layer_summary = summarize_service_layers(matrix)
    key_findings = make_key_findings(matrix, supplier_summary, domain_priority_summary, service_layer_summary, questions)

    supplier_summary.to_csv(processed_dir / "supplier_summary.csv", index=False)
    domain_priority_summary.to_csv(processed_dir / "domain_priority_summary.csv", index=False)
    service_layer_summary.to_csv(processed_dir / "service_layer_summary.csv", index=False)
    key_findings.to_csv(processed_dir / "key_findings.csv", index=False)

    print(f"[OK] wrote {processed_dir / 'supplier_summary.csv'} with {len(supplier_summary)} rows")
    print(f"[OK] wrote {processed_dir / 'domain_priority_summary.csv'} with {len(domain_priority_summary)} rows")
    print(f"[OK] wrote {processed_dir / 'service_layer_summary.csv'} with {len(service_layer_summary)} rows")
    print(f"[OK] wrote {processed_dir / 'key_findings.csv'} with {len(key_findings)} rows")


def main() -> None:
    parser = argparse.ArgumentParser(description="Vat soevereiniteitsanalyse samen voor rapportage")
    parser.add_argument("--processed-dir", default="data/processed/latest")
    args = parser.parse_args()
    run(Path(args.processed_dir))


if __name__ == "__main__":
    main()
