from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

import pandas as pd


def read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in list(df.columns):
        if col.startswith("Unnamed"):
            df = df.drop(columns=[col])
    return df


def safe_str(value) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def split_values(value: str) -> list[str]:
    value = safe_str(value)
    if not value:
        return []
    parts = re.split(r"[,|]", value)
    return [p.strip() for p in parts if p.strip()]


def load_catalog(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=["needle", "supplier_name", "category", "jurisdiction_hint", "verification_needed"])


def lookup_supplier(token: str, catalog: pd.DataFrame) -> dict:
    t = token.lower()
    for _, row in catalog.iterrows():
        needle = safe_str(row.get("needle", "")).lower()
        if needle and needle in t:
            return {
                "supplier_name": row.get("supplier_name", "Onbekend"),
                "category": row.get("category", "onbekend"),
                "jurisdiction_hint": row.get("jurisdiction_hint", "Onbekend"),
                "verification_needed": row.get("verification_needed", "ja"),
            }
    return {
        "supplier_name": "Onbekend",
        "category": "onbekend",
        "jurisdiction_hint": "Onbekend",
        "verification_needed": "ja",
    }


def is_truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return safe_str(value).strip().lower() in {"true", "1", "yes", "ja"}


def derive_mail_relevant(row: pd.Series) -> str:
    domain = safe_str(row.get("domain", ""))
    if domain.startswith("www."):
        return "waarschijnlijk nee"
    if safe_str(row.get("mx", "")) or safe_str(row.get("spf", "")) or safe_str(row.get("dmarc", "")):
        return "ja"
    if domain.startswith("formulieren.") or "mail" in domain:
        return "onbekend"
    return "onbekend"


def derive_risk_category(score: int) -> str:
    if score >= 60:
        return "hoog"
    if score >= 35:
        return "middel"
    return "laag"


def derive_review_priority(row: pd.Series) -> str:
    pd_likelihood = safe_str(row.get("personal_data_likelihood", "")).lower()
    score = int(row.get("risk_score", 0) or 0)
    sovereignty = " ".join([
        safe_str(row.get("sovereignty_hint", "")),
        safe_str(row.get("mail_sovereignty_hint", "")),
    ]).lower()

    if pd_likelihood in {"waarschijnlijk", "zeker"} and score >= 35:
        return "P1"
    if "vs leverancier" in sovereignty and pd_likelihood in {"mogelijk", "waarschijnlijk", "zeker"}:
        return "P1"
    if score >= 50:
        return "P1"
    if score >= 35 or "onbekend" in sovereignty:
        return "P2"
    return "P3"


def enrich_domain_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bool_cols = ["https_ok", "hsts", "csp", "x_frame_options", "referrer_policy", "permissions_policy", "security_txt"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].apply(is_truthy)

    if "risk_score" in df.columns:
        df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0).astype(int)
    else:
        df["risk_score"] = 0

    df["mail_relevant"] = df.apply(derive_mail_relevant, axis=1)
    df["risk_category"] = df["risk_score"].apply(derive_risk_category)
    df["review_priority"] = df.apply(derive_review_priority, axis=1)
    df["missing_hsts"] = ~df.get("hsts", pd.Series([False] * len(df)))
    df["missing_csp"] = ~df.get("csp", pd.Series([False] * len(df)))
    df["missing_security_txt"] = ~df.get("security_txt", pd.Series([False] * len(df)))
    df["dmarc_policy"] = df.get("dmarc", "").apply(lambda v: re.search(r"p=([^;]+)", safe_str(v), flags=re.I).group(1).lower() if re.search(r"p=([^;]+)", safe_str(v), flags=re.I) else "")
    df["dmarc_effective"] = df["dmarc_policy"].isin(["quarantine", "reject"])
    df["needs_woo_verification"] = df.apply(lambda r: "ja" if r["review_priority"] in {"P1", "P2"} or "Onbekend" in safe_str(r.get("sovereignty_hint", "")) else "nee", axis=1)
    df["enriched_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    return df


def build_supplier_table(df: pd.DataFrame, catalog: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        domain = safe_str(row.get("domain", ""))
        sources = {
            "MX": split_values(row.get("mx", "")),
            "SPF include": split_values(row.get("spf_includes", "")),
            "SPF ip4": split_values(row.get("spf_ip4s", "")),
            "SPF ip6": split_values(row.get("spf_ip6s", "")),
            "External script": split_values(row.get("external_script_domains", "")),
            "Tracker hint": split_values(row.get("tracker_hints", "")),
            "Hosting hint": split_values(row.get("hosting_hint", "")),
        }
        for source_type, values in sources.items():
            for value in values:
                match = lookup_supplier(value, catalog)
                rows.append({
                    "domain": domain,
                    "source_type": source_type,
                    "indicator": value,
                    **match,
                })
    out = pd.DataFrame(rows).drop_duplicates() if rows else pd.DataFrame()
    return out


def build_summary(enriched: pd.DataFrame, suppliers: pd.DataFrame) -> pd.DataFrame:
    metrics = {
        "domains_total": len(enriched),
        "https_ok": int(enriched.get("https_ok", pd.Series(dtype=bool)).sum()),
        "hsts_present": int(enriched.get("hsts", pd.Series(dtype=bool)).sum()),
        "csp_present": int(enriched.get("csp", pd.Series(dtype=bool)).sum()),
        "security_txt_present": int(enriched.get("security_txt", pd.Series(dtype=bool)).sum()),
        "dmarc_effective": int(enriched.get("dmarc_effective", pd.Series(dtype=bool)).sum()),
        "p1_items": int((enriched.get("review_priority") == "P1").sum()),
        "p2_items": int((enriched.get("review_priority") == "P2").sum()),
        "unique_supplier_indicators": int(suppliers["indicator"].nunique()) if not suppliers.empty else 0,
        "unknown_hosting_hint": int((enriched.get("hosting_hint", "") == "Onbekend").sum()) if "hosting_hint" in enriched.columns else 0,
    }
    return pd.DataFrame([{"metric": k, "value": v} for k, v in metrics.items()])


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich digitale footprint scan results")
    parser.add_argument("--input", required=True, help="Path to raw scanner CSV")
    parser.add_argument("--catalog", default="data/lookups/supplier_catalog.csv", help="Supplier catalog CSV")
    parser.add_argument("--output-dir", default="data/processed/latest", help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    catalog_path = Path(args.catalog)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = read_csv(input_path)
    catalog = load_catalog(catalog_path)
    enriched = enrich_domain_table(raw)
    suppliers = build_supplier_table(enriched, catalog)
    summary = build_summary(enriched, suppliers)

    enriched.to_csv(output_dir / "domains_enriched.csv", index=False)
    suppliers.to_csv(output_dir / "supplier_indicators.csv", index=False)
    summary.to_csv(output_dir / "summary.csv", index=False)

    print(f"Wrote {output_dir / 'domains_enriched.csv'}")
    print(f"Wrote {output_dir / 'supplier_indicators.csv'}")
    print(f"Wrote {output_dir / 'summary.csv'}")


if __name__ == "__main__":
    main()
