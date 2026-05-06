"""
scripts/generate_blog_pack.py

Genereert blogmateriaal, kernbevindingen en een Woo-vragenpakket
op basis van de processed CSV's.

Input uit data/processed/latest:
- key_findings.csv
- supplier_summary.csv
- domain_priority_summary.csv
- service_layer_summary.csv
- verification_questions.csv
- dataflow_matrix.csv

Output naar reports/:
- blog-outline.md
- key-findings.md
- woo-vragenpakket.md
- methodology-note.md

Gebruik:
    python scripts/generate_blog_pack.py \
      --processed-dir data/processed/latest \
      --reports-dir reports
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import pandas as pd


def clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def read_optional(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def metric(findings: pd.DataFrame, key: str, default: str = "0") -> str:
    if findings.empty or "finding" not in findings.columns or "value" not in findings.columns:
        return default
    rows = findings[findings["finding"] == key]
    if rows.empty:
        return default
    return clean(rows.iloc[0]["value"]) or default


def md_table(df: pd.DataFrame, columns: List[str], limit: int = 10) -> str:
    if df.empty:
        return "_Geen data beschikbaar._\n"
    available = [c for c in columns if c in df.columns]
    if not available:
        return "_Geen passende kolommen beschikbaar._\n"
    view = df[available].head(limit).copy()
    return view.to_markdown(index=False) + "\n"


def write_key_findings(reports_dir: Path, findings: pd.DataFrame, suppliers: pd.DataFrame, domains: pd.DataFrame, layers: pd.DataFrame) -> None:
    lines = []
    lines.append("# Kernbevindingen: digitale keten gemeente Huizen\n")
    lines.append("## Samenvatting\n")
    lines.append(f"- Onderzochte domeinen: **{metric(findings, 'onderzochte_domeinen')}**")
    lines.append(f"- Datastroomindicatoren: **{metric(findings, 'datastroom_indicatoren')}**")
    lines.append(f"- Unieke leveranciers of diensten: **{metric(findings, 'unieke_leveranciers')}**")
    lines.append(f"- Domeinen met US-leveranciersindicatie: **{metric(findings, 'domeinen_met_us_leveranciersindicatie')}**")
    lines.append(f"- P1-verificatievragen: **{metric(findings, 'p1_verificatievragen')}**")
    lines.append(f"- P2-verificatievragen: **{metric(findings, 'p2_verificatievragen')}**\n")

    lines.append("## Belangrijkste leveranciersindicatoren\n")
    lines.append(md_table(
        suppliers,
        [
            "supplier",
            "supplier_type",
            "jurisdiction_groups",
            "domains_count",
            "highest_data_risk",
            "p1_questions_count",
            "example_domains",
        ],
        limit=12,
    ))

    lines.append("## Domeinen met hoogste prioriteit\n")
    lines.append(md_table(
        domains,
        [
            "domain",
            "priority",
            "personal_data_likelihood",
            "us_supplier_count",
            "high_risk_supplier_count",
            "p1_questions_count",
            "priority_reason",
        ],
        limit=15,
    ))

    lines.append("## Service layers\n")
    lines.append(md_table(
        layers,
        [
            "service_layer",
            "domains_count",
            "suppliers_count",
            "indicator_count",
            "us_supplier_domains_count",
            "high_data_risk_domains_count",
            "top_suppliers",
        ],
        limit=10,
    ))

    lines.append("## Voorzichtige interpretatie\n")
    lines.append(
        "De analyse toont publieke indicatoren van betrokken leveranciers, diensten en technische ketens. "
        "Dit is geen sluitend bewijs van fysieke datalocatie of juridische doorgifte. Het laat wel zien waar aanvullende verificatie nodig is, "
        "bijvoorbeeld rond tenantregio, logging, back-ups, supporttoegang, subverwerkers en contractuele waarborgen.\n"
    )

    (reports_dir / "key-findings.md").write_text("\n".join(lines), encoding="utf-8")


def write_blog_outline(reports_dir: Path, findings: pd.DataFrame, suppliers: pd.DataFrame, domains: pd.DataFrame) -> None:
    top_suppliers = ", ".join(suppliers.get("supplier", pd.Series(dtype=str)).head(5).astype(str).tolist()) if not suppliers.empty else "Microsoft, Google, Cloudflare en andere leveranciers"
    p1_count = metric(findings, "p1_verificatievragen")
    domain_count = metric(findings, "onderzochte_domeinen")

    lines = []
    lines.append("# Blog-outline\n")
    lines.append("## Werktitel\n")
    lines.append("**De gemeentelijke website staat misschien in Nederland, maar waar loopt de digitale keten naartoe?**\n")

    lines.append("## Kernboodschap\n")
    lines.append(
        f"Voor gemeente Huizen zijn {domain_count} domeinen en gelieerde digitale diensten onderzocht. "
        "De scan laat zien dat hostinglocatie slechts één deel van het verhaal is. "
        "Via mail, formulieren, scripts, CDN's, analytics en SaaS ontstaat een bredere keten van leveranciers. "
        "Publiek is vaak zichtbaar dát zulke afhankelijkheden bestaan, maar niet welke data precies wordt verwerkt, waar logs en back-ups staan, "
        "of welke subverwerkers en supportconstructies worden gebruikt.\n"
    )

    lines.append("## Mogelijke inleiding\n")
    lines.append(
        "Wie de website van een gemeente bezoekt, verwacht waarschijnlijk bij de digitale overheid te zijn. "
        "Maar de moderne gemeentelijke website is zelden één website. Het is een netwerk van domeinen, formulieren, maildiensten, "
        "toegankelijkheidsdiensten, analytics, cloudplatforms, uitvoeringsorganisaties en leveranciers. "
        "De casus Huizen laat zien waarom een domeinenregister alleen niet genoeg is.\n"
    )

    lines.append("## Voorgestelde opbouw\n")
    sections = [
        ("1. Aanleiding", "Huizen lijkt geen volledig publiek domeinoverzicht via organisaties.overheid.nl te bieden. Dat maakt controle door inwoners lastiger."),
        ("2. Methode", "Niet-invasieve OSINT-analyse van domeinen, DNS, MX, SPF, HTTPS, headers, scripts, hosting- en leveranciersindicatoren."),
        ("3. Van website naar keten", "Leg uit dat inwoners niet alleen een webserver raken, maar ook maildiensten, scripts, CDN's, formulieren en SaaS."),
        ("4. Wat zichtbaar wordt", f"Noem de belangrijkste leveranciersindicatoren, bijvoorbeeld: {top_suppliers}."),
        ("5. Hosting is niet hetzelfde als soevereiniteit", "Een Nederlandse hoster sluit internationale cloud-, mail-, CDN- of SaaS-afhankelijkheden niet uit."),
        ("6. De privacyverklaring is niet de ketenkaart", "Een privacyverklaring kan juridisch nuttig zijn, maar vaak ontbreken concrete details over subverwerkers, logging, back-ups en supporttoegang."),
        ("7. Wat nog geverifieerd moet worden", f"De analyse levert {p1_count} P1-verificatievragen op. Die zijn geschikt als basis voor een Woo-verzoek."),
        ("8. Oplossing", "Gemeenten zouden een publieke digitale ketenkaart moeten publiceren: domeinen, leveranciers, datacategorieën, hosting, subverwerkers en verantwoordelijke partij."),
    ]
    for title, body in sections:
        lines.append(f"### {title}\n")
        lines.append(body + "\n")

    lines.append("## Belangrijke nuance\n")
    lines.append(
        "Schrijf niet dat alle gegevens buiten Europa worden verwerkt. De juiste conclusie is dat publieke indicatoren afhankelijkheden tonen van leveranciers "
        "met verschillende jurisdicties. Dat vraagt om verificatie van datalocatie, logging, back-ups, subverwerkers, supporttoegang en contractuele waarborgen.\n"
    )

    lines.append("## Mogelijke slotzin\n")
    lines.append(
        "> De vraag is niet alleen waar de website staat, maar welke digitale keten ontstaat zodra een inwoner een pagina opent, mailt, een formulier invult of een gemeentelijke dienst gebruikt.\n"
    )

    (reports_dir / "blog-outline.md").write_text("\n".join(lines), encoding="utf-8")


def write_woo_questions(reports_dir: Path, questions: pd.DataFrame, suppliers: pd.DataFrame, domains: pd.DataFrame) -> None:
    lines = []
    lines.append("# Woo-vragenpakket: digitale keten gemeente Huizen\n")
    lines.append("## Doel van het verzoek\n")
    lines.append(
        "Dit verzoek is bedoeld om de publieke digitale keten rond gemeente Huizen te verduidelijken. "
        "De publieke scan toont technische indicatoren, maar kan niet vaststellen waar data, logs en back-ups staan, "
        "welke subverwerkers betrokken zijn, welke contractuele waarborgen gelden en welke interne systemen gekoppeld zijn.\n"
    )

    lines.append("## Algemene vragen\n")
    general_questions = [
        "Graag een overzicht van alle domeinen en subdomeinen die gemeente Huizen beheert of laat beheren.",
        "Graag een overzicht van websites, SaaS-platformen en externe digitale diensten die worden gebruikt voor publieke dienstverlening.",
        "Graag per domein of dienst: verantwoordelijke organisatie, verwerker, leverancier, subverwerkers en doel van verwerking.",
        "Graag per domein of dienst: of persoonsgegevens worden verwerkt, welke categorieën persoonsgegevens, en of bijzondere of gevoelige gegevens kunnen voorkomen.",
        "Graag per domein of dienst: hostinglocatie, cloudregio, logginglocatie, back-uplocatie en bewaartermijnen.",
        "Graag per domein of dienst: of leveranciers of subverwerkers onder niet-EU jurisdictie vallen, en welke aanvullende waarborgen daarvoor zijn getroffen.",
        "Graag het beleid van de gemeente rond cloudgebruik, digitale soevereiniteit en inzet van niet-Europese leveranciers.",
        "Graag beschikbare DPIA's, risicoanalyses of BIO-classificaties voor de onderzochte digitale diensten, voor zover openbaar te maken.",
    ]
    for q in general_questions:
        lines.append(f"- {q}")
    lines.append("")

    lines.append("## Leveranciersgerichte vragen\n")
    if suppliers.empty:
        lines.append("_Geen leverancierssamenvatting beschikbaar._\n")
    else:
        for _, row in suppliers.head(15).iterrows():
            supplier = clean(row.get("supplier", ""))
            supplier_type = clean(row.get("supplier_type", ""))
            jurisdiction = clean(row.get("jurisdiction_groups", ""))
            domains_count = clean(row.get("domains_count", ""))
            typical_data = clean(row.get("typical_data", ""))
            lines.append(f"### {supplier}\n")
            lines.append(f"- Type: {supplier_type}")
            lines.append(f"- Jurisdictie-indicatie: {jurisdiction}")
            lines.append(f"- Aantal domeinen met indicator: {domains_count}")
            if typical_data:
                lines.append(f"- Mogelijke datacategorieën: {typical_data}")
            related = questions[questions.get("supplier", "") == supplier] if not questions.empty else pd.DataFrame()
            if related.empty:
                lines.append("- Welke rol heeft deze leverancier in de gemeentelijke digitale keten, en welke data wordt verwerkt?")
            else:
                for question in related.get("question", pd.Series(dtype=str)).dropna().drop_duplicates().head(5):
                    lines.append(f"- {clean(question)}")
            lines.append("")

    lines.append("## Domeinen met hoogste prioriteit\n")
    if domains.empty:
        lines.append("_Geen domeinprioriteiten beschikbaar._\n")
    else:
        for _, row in domains.head(12).iterrows():
            lines.append(
                f"- **{clean(row.get('domain', ''))}** ({clean(row.get('priority', ''))}): "
                f"{clean(row.get('priority_reason', ''))}"
            )
        lines.append("")

    lines.append("## Toelichting bij de publieke scan\n")
    lines.append(
        "De bijlage met publieke indicatoren is geen kwetsbaarheidsscan en bevat geen bewijs dat gegevens buiten de EU worden opgeslagen. "
        "De indicatoren tonen wel welke leveranciers en technische ketens publiek zichtbaar zijn. Het verzoek richt zich daarom op verificatie van de ontbrekende context.\n"
    )

    (reports_dir / "woo-vragenpakket.md").write_text("\n".join(lines), encoding="utf-8")


def write_methodology(reports_dir: Path) -> None:
    lines = []
    lines.append("# Methodologische notitie\n")
    lines.append("## Scope\n")
    lines.append(
        "De analyse brengt publiek zichtbare digitale ketenindicatoren in kaart rond gemeente Huizen, verbonden partijen, uitvoeringsorganisaties en leveranciersplatformen. "
        "De scope omvat domeinen, DNS, MX, SPF, HTTPS, HTTP-headers, scripts, CDN's, hosting- en leveranciersindicatoren.\n"
    )
    lines.append("## Wat de analyse wel zegt\n")
    lines.append("- Welke domeinen en leveranciersindicatoren publiek zichtbaar zijn.")
    lines.append("- Welke service layers zichtbaar worden, zoals mail, frontend scripts en hosting/netwerk.")
    lines.append("- Welke leveranciers nader geverifieerd moeten worden vanwege datarisico of jurisdictievragen.")
    lines.append("- Welke vragen geschikt zijn voor vervolganalyse of een Woo-verzoek.\n")
    lines.append("## Wat de analyse niet bewijst\n")
    lines.append("- Waar applicatiedata definitief wordt opgeslagen.")
    lines.append("- Waar logging, back-ups en monitoringdata staan.")
    lines.append("- Welke supporttoegang contractueel of technisch mogelijk is.")
    lines.append("- Welke subverwerkers formeel zijn afgesproken.")
    lines.append("- Of sprake is van een juridische doorgifte buiten de EER.\n")
    lines.append("## Belangrijke interpretatieregel\n")
    lines.append(
        "Een Amerikaanse leverancierindicator betekent niet automatisch dat persoonsgegevens buiten de EU worden opgeslagen. "
        "Het betekent wel dat er een relevante vraag bestaat over jurisdictie, datalocatie, logging, supporttoegang, subverwerkers en aanvullende waarborgen.\n"
    )
    (reports_dir / "methodology-note.md").write_text("\n".join(lines), encoding="utf-8")


def run(processed_dir: Path, reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)

    findings = read_optional(processed_dir / "key_findings.csv")
    suppliers = read_optional(processed_dir / "supplier_summary.csv")
    domains = read_optional(processed_dir / "domain_priority_summary.csv")
    layers = read_optional(processed_dir / "service_layer_summary.csv")
    questions = read_optional(processed_dir / "verification_questions.csv")

    write_key_findings(reports_dir, findings, suppliers, domains, layers)
    write_blog_outline(reports_dir, findings, suppliers, domains)
    write_woo_questions(reports_dir, questions, suppliers, domains)
    write_methodology(reports_dir)

    print(f"[OK] wrote {reports_dir / 'key-findings.md'}")
    print(f"[OK] wrote {reports_dir / 'blog-outline.md'}")
    print(f"[OK] wrote {reports_dir / 'woo-vragenpakket.md'}")
    print(f"[OK] wrote {reports_dir / 'methodology-note.md'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Genereer blogpakket en Woo-vragenpakket")
    parser.add_argument("--processed-dir", default="data/processed/latest")
    parser.add_argument("--reports-dir", default="reports")
    args = parser.parse_args()
    run(Path(args.processed_dir), Path(args.reports_dir))


if __name__ == "__main__":
    main()
