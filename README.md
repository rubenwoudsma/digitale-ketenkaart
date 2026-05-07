# Digitale Ketenkaart

> OSINT-pipeline voor het in kaart brengen van digitale overheidsketens, domeinen, leveranciers, datastromen, hostingindicatoren en soevereiniteitsvragen.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-data%20pipeline-150458?logo=pandas&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-automation-2088FF?logo=githubactions&logoColor=white) ![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-static%20site-222222?logo=githubpages&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-green)

## Waar is dit voor?

Deze repository bevat een reproduceerbare OSINT-pipeline om de publieke digitale footprint van een gemeente of publieke organisatie te analyseren.

De pipeline vertrekt vanuit ruwe scanresultaten en verrijkt deze stap voor stap tot:

* domeinoverzichten
* leveranciersindicatoren
* mailketen-analyse
* hosting- en netwerkindicaties
* datastroomindicatoren
* soevereiniteitsvragen
* prioriteitenlijsten
* Woo-verificatievragen
* Markdownrapporten
* een Streamlit-dashboard
* een statische GitHub Pages projectsite

De casus in deze repository is **gemeente Huizen**, maar de opzet is bedoeld om herbruikbaar te zijn voor andere gemeenten of publieke organisaties.

## Wat doet deze repo niet?

Deze repository is geen pentesttool, vulnerability scanner of compliance-oordeel.

De output is gebaseerd op publieke indicatoren, zoals DNS, MX, SPF, HTTP headers, externe scripts, hosting hints en zichtbare leverancierssporen.

De resultaten bewijzen niet:

* dat persoonsgegevens buiten de EU worden opgeslagen
* dat sprake is van een AVG-overtreding
* waar back-ups, logs of telemetrie exact staan
* welke subverwerkers contractueel zijn afgesproken
* welke supporttoegang leveranciers hebben
* welke interne applicaties gekoppeld zijn

De pipeline laat vooral zien **waar vervolgvragen nodig zijn**.

## Status

|Onderdeel|Status|
|-|-|
|Enrichment pipeline|Werkend|
|Streamlit dashboard|Werkend|
|GitHub Pages|Werkend|
|Woo-vragenpakket|Concept|
|Blogpost|Concept|
|Multi-gemeente ondersteuning|Experimenteel|

## Architectuur

```text
raw scan CSV
  |
  v
enrich\_results.py
  |
  +--> domains_enriched.csv
  +--> supplier_indicators.csv
  +--> summary.csv
  |
  v
enrich_network.py
  |
  +--> domains_network_enriched.csv
  +--> rdap_cache.json
  |
  v
enrich_sovereignty.py
  |
  +--> dataflow_matrix.csv
  +--> sovereignty_summary.csv
  +--> verification_questions.csv
  |
  v
summarize_sovereignty.py
  |
  +--> supplier_summary.csv
  +--> domain_priority_summary.csv
  +--> service_layer_summary.csv
  +--> key_findings.csv
  |
  v
generate_markdown_report.py
generate_blog_pack.py
generate_pages.py
  |
  +--> reports*.md
  +--> docs*.html
  |
  v
Streamlit dashboard
GitHub Pages
```

## Repository-structuur

```text
digitale-ketenkaart/
├── .github/
│   └── workflows/
│       ├── enrich.yml
│       └── pages.yml
├── data/
│   ├── lookups/
│   │   ├── supplier_catalog.csv
│   │   └── sovereignty_catalog.csv
│   ├── processed/
│   │   └── latest/
│   │       ├── dataflow_matrix.csv
│   │       ├── domain_priority_summary.csv
│   │       ├── domains_enriched.csv
│   │       ├── domains_network_enriched.csv
│   │       ├── key_findings.csv
│   │       ├── service_layer_summary.csv
│   │       ├── sovereignty_summary.csv
│   │       ├── summary.csv
│   │       ├── supplier_indicators.csv
│   │       ├── supplier_summary.csv
│   │       └── verification_questions.csv
│   └── raw/
│       └── 2026-05-06/
│           ├── digitale-footprint-gemeente-huizen.csv
│           └── digitale-footprint-hzn-prioriteiten.csv
├── docs/
│   ├── index.html
│   ├── resultaten.html
│   ├── methode.html
│   ├── ketenkaart.html
│   ├── woo.html
│   ├── downloads.html
│   ├── data/
│   └── reports/
├── reports/
│   ├── blog-outline.md
│   ├── key-findings.md
│   ├── latest-analysis.md
│   ├── methodology-note.md
│   └── woo-vragenpakket.md
├── scripts/
│   ├── enrich_results.py
│   ├── enrich_network.py
│   ├── enrich_sovereignty.py
│   ├── summarize_sovereignty.py
│   ├── generate_markdown_report.py
│   ├── generate_blog_pack.py
│   └── generate_pages.py
├── streamlit_app.py
├── requirements.txt
├── LICENSE
└── README.md
```

## Gebruikte technieken

|Tool|Gebruik|
|-|-|
|Python|Pipeline, parsing, verrijking en rapportgeneratie|
|Pandas|CSV-verwerking, aggregaties en samenvattingen|
|Streamlit|Interactief dashboard voor analyse en filtering|
|Altair|Grafieken in het Streamlit-dashboard|
|dnspython|DNS-, MX-, TXT- en SPF-informatie|
|requests|HTTP requests, RDAP en publieke endpoints|
|BeautifulSoup|Extractie van scripts, iframes en externe bronnen|
|Markdown|Genereren van rapporten en blogmateriaal|
|Jinja2|Genereren van statische GitHub Pages HTML|
|GitHub Actions|Automatisch draaien van enrichment en pages build|
|GitHub Pages|Statische projectsite en publieke referentie|
|Shields.io|Badges in deze README|

## Installatie

```bash
git clone https://github.com/rubenwoudsma/digitale-ketenkaart.git
cd digitale-ketenkaart

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Windows PowerShell:

```powershell
git clone https://github.com/rubenwoudsma/digitale-ketenkaart.git
cd digitale-ketenkaart

python -m venv .venv
.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
```

## Pipeline lokaal draaien

### 1\. Domeinen verrijken

```bash
python scripts/enrich_results.py \\
  --input data/raw/2026-05-06/digitale-footprint-gemeente-huizen.csv \\
  --catalog data/lookups/supplier_catalog.csv \\
  --output-dir data/processed/latest
```

Output:

```text
data/processed/latest/domains_enriched.csv
data/processed/latest/supplier_indicators.csv
data/processed/latest/summary.csv
```

### 2\. Netwerk- en hostinginformatie verrijken

```bash
python scripts/enrich_network.py \\
  --input data/processed/latest/domains_enriched.csv \\
  --output data/processed/latest/domains_network_enriched.csv
```

Output:

```text
data/processed/latest/domains_network_enriched.csv
data/processed/latest/rdap_cache.json
```

### 3\. Soevereiniteitsanalyse maken

```bash
python scripts/enrich_sovereignty.py \\
  --domains data/processed/latest/domains_network_enriched.csv \\
  --suppliers data/processed/latest/supplier_indicators.csv \\
  --catalog data/lookups/sovereignty_catalog.csv \\
  --output-dir data/processed/latest
```

Output:

```text
data/processed/latest/dataflow_matrix.csv
data/processed/latest/sovereignty_summary.csv
data/processed/latest/verification_questions.csv
```

### 4\. Samenvattingen maken

```bash
python scripts/summarize_sovereignty.py \\
  --processed-dir data/processed/latest
```

Output:

```text
data/processed/latest/supplier_summary.csv
data/processed/latest/domain_priority_summary.csv
data/processed/latest/service_layer_summary.csv
data/processed/latest/key_findings.csv
```

### 5\. Rapporten genereren

```bash
python scripts/generate_markdown_report.py \\
  --processed-dir data/processed/latest \\
  --output reports/latest-analysis.md

python scripts/generate_blog_pack.py \\
  --processed-dir data/processed/latest \\
  --reports-dir reports
```

Output:

```text
reports/latest-analysis.md
reports/key-findings.md
reports/blog-outline.md
reports/woo-vragenpakket.md
reports/methodology-note.md
```

### 6\. GitHub Pages-site genereren

```bash
python scripts/generate_pages.py
```

Output:

```text
docs/index.html
docs/resultaten.html
docs/methode.html
docs/ketenkaart.html
docs/woo.html
docs/downloads.html
docs/data/*.csv
docs/reports/*.md
```

## Alles lokaal achter elkaar draaien

```bash
python scripts/enrich_results.py \\
  --input data/raw/2026-05-06/digitale-footprint-gemeente-huizen.csv \\
  --catalog data/lookups/supplier_catalog.csv \\
  --output-dir data/processed/latest

python scripts/enrich_network.py \\
  --input data/processed/latest/domains_enriched.csv \\
  --output data/processed/latest/domains_network_enriched.csv

python scripts/enrich\_sovereignty.py \\
  --domains data/processed/latest/domains_network_enriched.csv \\
  --suppliers data/processed/latest/supplier_indicators.csv \\
  --catalog data/lookups/sovereignty_catalog.csv \\
  --output-dir data/processed/latest

python scripts/summarize_sovereignty.py \\
  --processed-dir data/processed/latest

python scripts/generate_markdown_report.py \\
  --processed-dir data/processed/latest \\
  --output reports/latest-analysis.md

python scripts/generate_blog_pack.py \\
  --processed-dir data/processed/latest \\
  --reports-dir reports

python scripts/generate_pages.py
```

## Streamlit-dashboard

Start het interactieve dashboard lokaal:

```bash
streamlit run streamlit_app.py
```

Het dashboard gebruikt standaard:

```text
data/processed/latest/
reports/
```

Belangrijkste tabbladen:

|Tabblad|Doel|
|-|-|
|Overzicht|Publieke samenvatting en kerncijfers|
|Ketenkaart|Grafieken voor domeinen, leveranciers en ketenlagen|
|Domeinen|Filteren op domein, prioriteit en rol in de publieke keten|
|Leveranciers|Analyse van zichtbare leveranciers en diensten|
|Datastromen|Onderliggende datastroomindicatoren|
|Verificatievragen|Vragen voor Woo, leveranciers of vervolgonderzoek|
|Data|Controle en download van datasets|

## GitHub Actions

### Enrichment workflow

De workflow staat in:

```text
.github/workflows/enrich.yml
```

Deze workflow kan handmatig worden gestart via de GitHub Actions-tab.

De workflow draait de pipeline en uploadt de resultaten als workflow artifact.

Typische stappen:

```text
enrich_results.py
enrich_network.py
enrich_sovereignty.py
summarize_sovereignty.py
generate_markdown_report.py
generate_blog_pack.py
```

### Pages workflow

De workflow staat in:

```text
.github/workflows/pages.yml
```

Deze workflow genereert de statische site in `docs/` en publiceert deze via GitHub Pages.

## Belangrijkste datasets

### `domains_enriched.csv`

Verrijkte domeintabel met basisinformatie, mailrecords, security headers, hosting hints en risicosignalen.

### `domains_network_enriched.csv`

Uitbreiding van `domains\_enriched.csv` met RDAP-, netwerk-, hosting- en jurisdictie-indicaties.

### `supplier_indicators.csv`

Genormaliseerde indicatoren van leveranciers uit MX, SPF, externe scripts, tracker hints en hostingvelden.

### `dataflow_matrix.csv`

Onderzoeksdataset waarin domeinen, leveranciers, service layers, jurisdictie-indicaties en mogelijke datacategorieën samenkomen.

### `domain_priority_summary.csv`

Samenvatting per domein, geschikt voor dashboard en prioritering.

Bevat onder andere:

```text
domain
priority
public_service_layer
personal_data_likelihood
us_supplier_count
high_risk_supplier_count
p1_questions_count
priority_reason
```

### `supplier_summary.csv`

Samenvatting per leverancier of dienst.

Bevat onder andere:

```text
supplier
supplier_type
jurisdiction_groups
domains_count
indicator_count
service_layers
highest_data_risk
p1_questions_count
typical_data
example_domains
```

### `verification_questions.csv`

Concrete vragen voor verificatie bij gemeente, leveranciers of via een Woo-verzoek.

Prioriteiten:

|Prioriteit|Betekenis|
|-|-|
|P1|Als eerste uitzoeken|
|P2|Relevant vervolgonderzoek|
|P3|Lagere prioriteit, nuttig voor volledigheid|

Een P1-vraag betekent niet dat er iets fout is. Het betekent dat de combinatie van leverancier, datarisico en publieke dienstverlening om verduidelijking vraagt.

## Datamodel

De pipeline werkt grofweg met deze concepten:

```text
Domain
  -> Service layer
  -> Supplier indicator
  -> Supplier
  -> Jurisdiction hint
  -> Data risk hint
  -> Verification question
```

### Service layers

|Service layer|Betekenis|
|-|-|
|mx_spf|Mailketen, bijvoorbeeld MX en SPF|
|frontend_scripts|Scripts, embeds, analytics, tag managers|
|network_hosting|Hosting, CDN, WAF, ASN, RDAP|
|unknown|Niet eenduidig te classificeren|

### Indicatoren

Indicatoren kunnen onder andere komen uit:

```text
MX records
SPF includes
SPF ip4/ip6
CNAME
nameservers
server headers
external_script_domains
tracker_hints
hosting_hint
network_provider_hint
cloud_or_cdn_hint
```

## Interpretatie

Deze repository maakt onderscheid tussen:

```text
publiek zichtbaar
aannemelijk
te verifiëren
bevestigd
```

De huidige pipeline werkt vooral met de eerste drie categorieën. Bevestiging vraagt aanvullende bronnen, bijvoorbeeld:

* gemeentelijke documentatie
* verwerkersovereenkomsten
* subverwerkerslijsten
* DPIA’s
* BIO-classificaties
* cloudbeleid
* Woo-documenten
* leveranciersinformatie

## Onderzoeksethiek

Deze pipeline is ontworpen voor passieve en niet-invasieve analyse.

Doe wel:

* publieke DNS-informatie opvragen
* publieke HTTP headers bekijken
* externe scripts inventariseren
* RDAP of WHOIS-achtige bronnen raadplegen
* openbare rapportages en privacyverklaringen analyseren

Doe niet zonder toestemming:

* brute forcing
* vulnerability scanning
* exploit testing
* credential testing
* agressieve crawling
* omzeilen van toegangsbeperkingen
* testen van formulieren met echte persoonsgegevens

## Hergebruik voor een andere gemeente

1. Maak een nieuwe raw scan CSV.
2. Zet deze in `data/raw/<datum>/`.
3. Pas eventueel `supplier_catalog.csv` en `sovereignty_catalog.csv` aan.
4. Draai de pipeline opnieuw.
5. Controleer de output handmatig.
6. Publiceer alleen met duidelijke methodologische nuance.

Voorbeeld:

```bash
python scripts/enrich_results.py \\
  --input data/raw/2026-05-07/digitale-footprint-gemeente-x.csv \\
  --catalog data/lookups/supplier_catalog.csv \\
  --output-dir data/processed/latest
```

Daarna de rest van de pipeline draaien zoals hierboven.

## Methodologische beperkingen

De analyse is afhankelijk van publieke indicatoren. Daardoor zijn er belangrijke beperkingen:

* IP-locatie is niet hetzelfde als juridische datalocatie.
* CDN’s kunnen de daadwerkelijke origin hosting maskeren.
* SPF toont geautoriseerde mailverzenders, maar niet alle datastromen.
* Externe scripts tonen browserafhankelijkheden, maar niet altijd wat precies wordt verwerkt.
* Microsoft 365, Google Workspace en SaaS-diensten vereisen tenant- en contractinformatie voor harde conclusies.
* Subverwerkers zijn meestal niet volledig zichtbaar uit OSINT.
* Back-ups, logging en supporttoegang zijn vrijwel nooit publiek sluitend vast te stellen.

## Publicatiekanalen

|Kanaal|Doel|
|-|-|
|GitHub repo|Broncode, data en reproduceerbaarheid|
|GitHub Pages|Statische projectsite, methode en downloads|
|Streamlit|Interactieve analyse en dashboard|
|Blogpost|Narratief, duiding en maatschappelijke context|
|Woo-verzoek|Verificatie van ontbrekende context|

## Links

* GitHub repo: https://github.com/rubenwoudsma/digitale-ketenkaart
* Streamlit dashboard: https://digitale-ketenkaart.streamlit.app/
* GitHub Pages: https://rubenwoudsma.github.io/digitale-ketenkaart/
* Blog: https://rubenwoudsma.nl/

## Licentie

Deze repository is gepubliceerd onder de licentie in `LICENSE`.

## Disclaimer

Deze repository is bedoeld voor transparantieonderzoek, reproduceerbare OSINT en publieke verantwoording.

De resultaten zijn onderzoeksindicatoren. Ze zijn geen juridisch oordeel, geen beveiligingsaudit, geen pentest en geen definitief bewijs van dataverwerking buiten Nederland, de EU of de EER.
