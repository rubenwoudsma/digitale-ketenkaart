from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def read(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate markdown report from enriched data")
    parser.add_argument("--processed-dir", default="data/processed/latest")
    parser.add_argument("--output", default="reports/latest-analysis.md")
    args = parser.parse_args()

    processed = Path(args.processed_dir)
    domains = read(processed / "domains_enriched.csv")
    suppliers = read(processed / "supplier_indicators.csv")
    summary = read(processed / "summary.csv")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Eerste verrijkte analyse digitale footprint gemeente Huizen")
    lines.append("")
    lines.append("Dit rapport is automatisch gegenereerd op basis van publieke, niet-invasieve controles.")
    lines.append("")

    if not summary.empty:
        lines.append("## Samenvatting")
        lines.append("")
        lines.append("| Metric | Waarde |")
        lines.append("|---|---:|")
        for _, row in summary.iterrows():
            lines.append(f"| {row['metric']} | {row['value']} |")
        lines.append("")

    if not domains.empty:
        top = domains.sort_values(["review_priority", "risk_score"], ascending=[True, False]).head(12)
        lines.append("## Prioriteiten voor handmatige verificatie")
        lines.append("")
        lines.append("| Prioriteit | Domein | Score | Laag | Persoonsgegevens | Hosting | Soevereiniteit |")
        lines.append("|---|---|---:|---|---|---|---|")
        for _, row in top.iterrows():
            lines.append(
                f"| {row.get('review_priority','')} | {row.get('domain','')} | {row.get('risk_score','')} | "
                f"{row.get('layer','')} | {row.get('personal_data_likelihood','')} | "
                f"{row.get('hosting_hint','')} | {row.get('sovereignty_hint','')} |"
            )
        lines.append("")

    if not suppliers.empty:
        known = suppliers[suppliers["supplier_name"] != "Onbekend"]
        lines.append("## Herkende leveranciersindicatoren")
        lines.append("")
        lines.append("| Leverancier | Categorie | Jurisdictiehint | Aantal domeinen |")
        lines.append("|---|---|---|---:|")
        if not known.empty:
            grouped = known.groupby(["supplier_name", "category", "jurisdiction_hint"])["domain"].nunique().reset_index(name="domains")
            grouped = grouped.sort_values("domains", ascending=False)
            for _, row in grouped.iterrows():
                lines.append(f"| {row['supplier_name']} | {row['category']} | {row['jurisdiction_hint']} | {row['domains']} |")
        lines.append("")

    lines.append("## Beperkingen")
    lines.append("")
    lines.append("Een publieke scan kan aanwijzingen geven over hosting, afhankelijkheden en basisbeveiliging, maar kan geen sluitende uitspraak doen over datalocatie, logging, back-ups, supporttoegang, verwerkersovereenkomsten of subverwerkers. Daarvoor zijn aanvullende documenten van de gemeente of leveranciers nodig.")
    lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
