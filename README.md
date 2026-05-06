Digitale Ketenkaart, pipeline starter
Deze repo bevat een basispipeline om ruwe scanresultaten te verrijken tot analysebestanden en een Markdownrapport.
Lokaal draaien
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/enrich_results.py --input data/raw/2026-05-06/digitale-footprint-gemeente-huizen.csv --output-dir data/processed/latest
python scripts/generate_markdown_report.py --processed-dir data/processed/latest --output reports/latest-analysis.md
```
GitHub Actions
De workflow staat in `.github/workflows/enrich.yml` en kan handmatig worden gestart via de Actions-tab. Gebruik `workflow_dispatch` en geef eventueel het pad naar de raw CSV mee.
De workflow schrijft de resultaten niet automatisch terug naar de repo, maar uploadt ze als workflow artifact. Dat is veiliger voor de eerste fase.
Dataflow
```text
raw scan CSV
  -> domains_enriched.csv
  -> supplier_indicators.csv
  -> summary.csv
  -> latest-analysis.md
```
Beperking
De resultaten zijn indicaties uit publieke bronnen. Voor datalocatie, logging, back-ups, supporttoegang, subverwerkers en contractuele waarborgen is aanvullende verificatie nodig.
