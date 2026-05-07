from __future__ import annotations

from pathlib import Path
import shutil
import pandas as pd
import markdown
from jinja2 import Template

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed" / "latest"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

STREAMLIT_URL = "https://digitale-ketenkaart.streamlit.app/"
BLOG_URL = "https://rubenwoudsma.nl/"
GITHUB_URL = "https://github.com/rubenwoudsma/digitale-ketenkaart"

BASE_CSS = """
:root {
  --bg: #f8fafc;
  --card: #ffffff;
  --text: #0f172a;
  --muted: #475569;
  --border: #dbe3ef;
  --accent: #1d4ed8;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
header {
  background: #0f172a;
  color: white;
  padding: 48px 24px;
}
main {
  max-width: 1120px;
  margin: 0 auto;
  padding: 32px 20px 64px;
}
nav {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}
nav a, .button {
  display: inline-block;
  background: var(--accent);
  color: white;
  padding: 10px 14px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
}
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 22px;
  margin: 18px 0;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.metric {
  font-size: 34px;
  font-weight: 800;
}
.muted { color: var(--muted); }
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 14px;
  overflow: hidden;
}
th, td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  vertical-align: top;
}
th { background: #eef4ff; }
code {
  background: #e2e8f0;
  padding: 2px 5px;
  border-radius: 5px;
}
footer {
  border-top: 1px solid var(--border);
  padding: 24px;
  color: var(--muted);
}
.warning {
  border-left: 5px solid #f59e0b;
  background: #fffbeb;
}
"""

PAGE_TEMPLATE = Template("""
<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{{ description }}">
  <style>{{ css }}</style>
</head>
<body>
<header>
  <h1>{{ heading }}</h1>
  <p>{{ intro }}</p>
  <nav>
    <a href="index.html">Overzicht</a>
    <a href="resultaten.html">Resultaten</a>
    <a href="methode.html">Methode</a>
    <a href="ketenkaart.html">Ketenkaart</a>
    <a href="woo.html">Woo-vragen</a>
    <a href="downloads.html">Downloads</a>
    <a href="{{ streamlit_url }}">Interactieve app</a>
    <a href="{{ github_url }}">GitHub</a>
  </nav>
</header>
<main>
{{ body }}
</main>
<footer>
  Digitale Ketenkaart Gemeente Huizen, publieke OSINT-analyse. Indicatoren zijn onderzoekssignalen, geen bewijs van overtredingen.
</footer>
</body>
</html>
""")

def read_csv(name: str) -> pd.DataFrame:
    path = PROCESSED / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

def read_md(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "fenced_code"])

def table_html(df: pd.DataFrame, cols: list[str], limit: int = 10) -> str:
    if df.empty:
        return "<p><em>Geen data beschikbaar.</em></p>"
    available = [c for c in cols if c in df.columns]
    if not available:
        return "<p><em>Geen passende kolommen beschikbaar.</em></p>"
    return df[available].head(limit).to_html(index=False, escape=True)

def metric_value(key_findings: pd.DataFrame, key: str, default: str = "0") -> str:
    if key_findings.empty or "finding" not in key_findings.columns:
        return default
    rows = key_findings[key_findings["finding"] == key]
    if rows.empty:
        return default
    return str(rows.iloc[0]["value"])

def write_page(filename: str, title: str, heading: str, intro: str, body: str) -> None:
    html = PAGE_TEMPLATE.render(
        title=title,
        heading=heading,
        intro=intro,
        body=body,
        css=BASE_CSS,
        description="Publieke digitale ketenkaart rond gemeente Huizen",
        streamlit_url=STREAMLIT_URL,
        github_url=GITHUB_URL,
    )
    (DOCS / filename).write_text(html, encoding="utf-8")

def copy_downloads() -> None:
    data_dir = DOCS / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    for name in [
        "domain_priority_summary.csv",
        "supplier_summary.csv",
        "service_layer_summary.csv",
        "dataflow_matrix.csv",
        "verification_questions.csv",
        "key_findings.csv",
        "sovereignty_summary.csv",
    ]:
        src = PROCESSED / name
        if src.exists():
            shutil.copy2(src, data_dir / name)

    reports_dir = DOCS / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    for name in [
        "key-findings.md",
        "blog-outline.md",
        "woo-vragenpakket.md",
        "methodology-note.md",
        "latest-analysis.md",
    ]:
        src = REPORTS / name
        if src.exists():
            shutil.copy2(src, reports_dir / name)

def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "assets").mkdir(exist_ok=True)
    copy_downloads()

    key_findings = read_csv("key_findings.csv")
    suppliers = read_csv("supplier_summary.csv")
    domains = read_csv("domain_priority_summary.csv")
    layers = read_csv("service_layer_summary.csv")

    home_body = f"""
    <section class="card">
      <h2>Waarom deze site?</h2>
      <p>
        Deze projectsite hoort bij een onderzoek naar de digitale keten rond gemeente Huizen.
        De interactieve Streamlit-app is handig om te filteren en te analyseren.
        Deze pagina is bedoeld als rustige, citeerbare en langdurige publieksreferentie.
      </p>
    </section>

    <section class="grid">
      <div class="card"><div class="metric">{metric_value(key_findings, "onderzochte_domeinen")}</div><p>onderzochte domeinen</p></div>
      <div class="card"><div class="metric">{metric_value(key_findings, "datastroom_indicatoren")}</div><p>datastroomindicatoren</p></div>
      <div class="card"><div class="metric">{metric_value(key_findings, "unieke_leveranciers")}</div><p>zichtbare leveranciers of diensten</p></div>
      <div class="card"><div class="metric">{metric_value(key_findings, "p1_verificatievragen")}</div><p>P1-verificatievragen</p></div>
    </section>

    <section class="card warning">
      <h2>Belangrijke nuance</h2>
      <p>
        Deze analyse toont publieke technische indicatoren. Dat is geen bewijs dat persoonsgegevens buiten Europa worden opgeslagen
        en ook geen bewijs van een overtreding. De indicatoren laten zien waar extra uitleg en verificatie nodig zijn.
      </p>
    </section>

    <section class="card">
      <h2>Wat is een digitale ketenkaart?</h2>
      <p>
        Een digitale ketenkaart laat per digitale dienst zien welke domeinen, organisaties, leveranciers,
        verwerkers, hostinglocaties, datastromen en verificatievragen betrokken zijn.
      </p>
    </section>
    """
    write_page(
        "index.html",
        "Digitale Ketenkaart Gemeente Huizen",
        "Digitale Ketenkaart Gemeente Huizen",
        "Een publieke referentie over websites, leveranciers en digitale afhankelijkheden rond gemeente Huizen.",
        home_body,
    )

    results_body = f"""
    <section class="card">
      <h2>Domeinen die als eerste uitleg vragen</h2>
      {table_html(domains, ["domain", "priority", "public_service_layer", "us_supplier_count", "high_risk_supplier_count", "p1_questions_count", "priority_reason"], 15)}
    </section>
    <section class="card">
      <h2>Meest zichtbare leveranciers</h2>
      {table_html(suppliers, ["supplier", "supplier_type", "jurisdiction_groups", "domains_count", "highest_data_risk", "p1_questions_count"], 15)}
    </section>
    <section class="card">
      <h2>Ketenlagen</h2>
      {table_html(layers, ["service_layer", "domains_count", "suppliers_count", "indicator_count", "us_supplier_domains_count", "high_data_risk_domains_count"], 10)}
    </section>
    """
    write_page(
        "resultaten.html",
        "Resultaten",
        "Resultaten",
        "Samenvatting van de belangrijkste publieke indicatoren.",
        results_body,
    )

    methode_body = md_to_html(read_md(REPORTS / "methodology-note.md"))
    write_page(
        "methode.html",
        "Methode",
        "Methode",
        "Hoe de analyse is uitgevoerd en wat de analyse wel en niet bewijst.",
        f'<section class="card">{methode_body}</section>',
    )

    ketenkaart_body = """
    <section class="card">
      <h2>Voorgesteld model</h2>
      <p>
        De digitale ketenkaart is bedoeld als aanvulling op privacyverklaringen en domeinregistraties.
        Het domeinenregister laat zien welke voordeuren officieel zijn.
        De privacyverklaring beschrijft juridisch hoe met persoonsgegevens wordt omgegaan.
        De ketenkaart laat zien welke partijen en technische diensten achter een digitale dienst betrokken zijn.
      </p>
    </section>
    <section class="card">
      <h2>Minimale velden per digitale dienst</h2>
      <ul>
        <li>Domein of URL</li>
        <li>Doel van de dienst</li>
        <li>Verantwoordelijke organisatie</li>
        <li>Rol van de gemeente</li>
        <li>Leveranciers en verwerkers</li>
        <li>Relevante subverwerkers</li>
        <li>Gegevenscategorieën</li>
        <li>Hostinglocatie en cloudregio</li>
        <li>Jurisdictie van leveranciers</li>
        <li>Beveiligingsstandaarden</li>
        <li>Laatst gecontroleerd</li>
        <li>Verificatiestatus</li>
      </ul>
    </section>
    """
    write_page(
        "ketenkaart.html",
        "Ketenkaart",
        "Publieke digitale ketenkaart",
        "Een voorstel voor transparantie per digitale overheidsdienst.",
        ketenkaart_body,
    )

    woo_body = md_to_html(read_md(REPORTS / "woo-vragenpakket.md"))
    write_page(
        "woo.html",
        "Woo-vragenpakket",
        "Woo-vragenpakket",
        "Vragen om publieke indicatoren te verifiëren bij gemeente en leveranciers.",
        f'<section class="card">{woo_body}</section>',
    )

    downloads_body = """
    <section class="card">
      <h2>Data</h2>
      <ul>
        <li><a href="data/domain_priority_summary.csv">domain_priority_summary.csv</a></li>
        <li><a href="data/supplier_summary.csv">supplier_summary.csv</a></li>
        <li><a href="data/service_layer_summary.csv">service_layer_summary.csv</a></li>
        <li><a href="data/dataflow_matrix.csv">dataflow_matrix.csv</a></li>
        <li><a href="data/verification_questions.csv">verification_questions.csv</a></li>
        <li><a href="data/key_findings.csv">key_findings.csv</a></li>
      </ul>
    </section>
    <section class="card">
      <h2>Rapporten</h2>
      <ul>
        <li><a href="reports/key-findings.md">key-findings.md</a></li>
        <li><a href="reports/methodology-note.md">methodology-note.md</a></li>
        <li><a href="reports/woo-vragenpakket.md">woo-vragenpakket.md</a></li>
        <li><a href="reports/latest-analysis.md">latest-analysis.md</a></li>
      </ul>
    </section>
    """
    write_page(
        "downloads.html",
        "Downloads",
        "Downloads",
        "Machineleesbare data en rapportages.",
        downloads_body,
    )

    print(f"[OK] generated GitHub Pages site in {DOCS}")

if __name__ == "__main__":
    main()
