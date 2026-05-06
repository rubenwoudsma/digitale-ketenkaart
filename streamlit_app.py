"""
streamlit_app.py

Dashboard voor de Digitale Ketenkaart.

Doel:
- Processed CSV's tonen uit data/processed/latest
- Domeinen, leveranciers, datastromen, soevereiniteit en Woo-vragen analyseren
- Blog- en rapportmateriaal zichtbaar maken

Benodigde bestanden, indien aanwezig:
- data/processed/latest/domains_enriched.csv
- data/processed/latest/domains_network_enriched.csv
- data/processed/latest/dataflow_matrix.csv
- data/processed/latest/verification_questions.csv
- data/processed/latest/supplier_summary.csv
- data/processed/latest/domain_priority_summary.csv
- data/processed/latest/service_layer_summary.csv
- data/processed/latest/key_findings.csv
- reports/key-findings.md
- reports/blog-outline.md
- reports/woo-vragenpakket.md
- reports/methodology-note.md

Installatie:
    pip install -r requirements.txt

Starten:
    streamlit run streamlit_app.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd
import streamlit as st


APP_TITLE = "Digitale Ketenkaart"
DEFAULT_PROCESSED_DIR = Path("data/processed/latest")
DEFAULT_REPORTS_DIR = Path("reports")


CSV_FILES = {
    "domains_enriched": "domains_enriched.csv",
    "domains_network_enriched": "domains_network_enriched.csv",
    "dataflow_matrix": "dataflow_matrix.csv",
    "verification_questions": "verification_questions.csv",
    "supplier_summary": "supplier_summary.csv",
    "domain_priority_summary": "domain_priority_summary.csv",
    "service_layer_summary": "service_layer_summary.csv",
    "key_findings": "key_findings.csv",
    "summary": "summary.csv",
    "sovereignty_summary": "sovereignty_summary.csv",
}

REPORT_FILES = {
    "Kernbevindingen": "key-findings.md",
    "Blog-outline": "blog-outline.md",
    "Woo-vragenpakket": "woo-vragenpakket.md",
    "Methodologie": "methodology-note.md",
    "Laatste analyse": "latest-analysis.md",
}


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧭",
    layout="wide",
)


# -----------------------------
# Helpers
# -----------------------------


def clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


@st.cache_data(show_spinner=False)
def read_csv_cached(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_csv(file_path)


@st.cache_data(show_spinner=False)
def read_text_cached(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8")


def load_data(processed_dir: Path) -> Dict[str, pd.DataFrame]:
    return {
        key: read_csv_cached(str(processed_dir / filename))
        for key, filename in CSV_FILES.items()
    }


def load_reports(reports_dir: Path) -> Dict[str, str]:
    return {
        title: read_text_cached(str(reports_dir / filename))
        for title, filename in REPORT_FILES.items()
    }


def has_columns(df: pd.DataFrame, columns: Iterable[str]) -> bool:
    return all(c in df.columns for c in columns)


def metric_from_key_findings(key_findings: pd.DataFrame, finding: str, default: object = 0) -> object:
    if key_findings.empty or not has_columns(key_findings, ["finding", "value"]):
        return default
    rows = key_findings[key_findings["finding"] == finding]
    if rows.empty:
        return default
    return rows.iloc[0]["value"]


def dataframe_download(df: pd.DataFrame, label: str, filename: str) -> None:
    if df.empty:
        return
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


def filter_text(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if df.empty or not query.strip():
        return df
    q = query.lower().strip()
    mask = df.astype(str).apply(lambda col: col.str.lower().str.contains(q, na=False, regex=False)).any(axis=1)
    return df[mask]


def priority_badge_text(priority: str) -> str:
    priority = clean(priority).upper()
    if priority == "P1":
        return "P1, hoogste prioriteit"
    if priority == "P2":
        return "P2, nader onderzoeken"
    if priority == "P3":
        return "P3, lagere prioriteit"
    return priority or "Onbekend"


def sort_by_priority(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "priority" not in df.columns:
        return df
    order = {"P1": 1, "P2": 2, "P3": 3}
    result = df.copy()
    result["_priority_order"] = result["priority"].map(order).fillna(9)
    sort_cols = ["_priority_order"]
    for col in ["p1_questions_count", "us_supplier_count", "high_risk_supplier_count", "domains_count"]:
        if col in result.columns:
            sort_cols.append(col)
    ascending = [True] + [False] * (len(sort_cols) - 1)
    return result.sort_values(sort_cols, ascending=ascending).drop(columns=["_priority_order"])


def show_missing_file_notice(name: str, path: Path) -> None:
    st.info(f"Bestand niet gevonden voor `{name}`: `{path}`. Draai eerst de pipeline of controleer het pad.")


def compact_columns(df: pd.DataFrame, preferred: List[str]) -> pd.DataFrame:
    if df.empty:
        return df
    cols = [c for c in preferred if c in df.columns]
    return df[cols] if cols else df


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("Digitale Ketenkaart")
st.sidebar.caption("Een publieksdashboard over websites, leveranciers en digitale afhankelijkheden rond gemeente Huizen.")

processed_dir = DEFAULT_PROCESSED_DIR
reports_dir = DEFAULT_REPORTS_DIR

if st.sidebar.button("Data opnieuw laden", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("**Belangrijke nuance**")
st.sidebar.caption(
    "Deze kaart toont publieke aanwijzingen voor digitale afhankelijkheden. Het is geen bewijs dat gegevens buiten Europa worden opgeslagen. "
    "Daarvoor zijn contracten, verwerkersafspraken en informatie van de gemeente nodig."
)


# -----------------------------
# Load
# -----------------------------

data = load_data(processed_dir)
reports = load_reports(reports_dir)

key_findings = data["key_findings"]
supplier_summary = data["supplier_summary"]
domain_priority = data["domain_priority_summary"]
service_layers = data["service_layer_summary"]
dataflow = data["dataflow_matrix"]
questions = data["verification_questions"]
domains_network = data["domains_network_enriched"]
domains_enriched = data["domains_enriched"]


# -----------------------------
# Header
# -----------------------------

st.title("Digitale Ketenkaart gemeente Huizen")
st.caption(
    "Wie online contact heeft met de gemeente, gebruikt vaak meer dan één gemeentelijke website. Dit dashboard laat zien welke websites, leveranciers en technische diensten publiek zichtbaar zijn in de digitale keten rond Huizen."
)

if all(df.empty for df in data.values()):
    st.warning("Er zijn nog geen processed CSV's gevonden. Controleer het pad of draai eerst de pipeline.")
    st.stop()


# -----------------------------
# Tabs
# -----------------------------

tabs = st.tabs(
    [
        "Overzicht",
        "Domeinen",
        "Leveranciers",
        "Datastromen",
        "Verificatievragen",
        "Data",
    ]
)


# -----------------------------
# Overview
# -----------------------------

with tabs[0]:
    st.subheader("Wat is onderzocht?")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Onderzochte domeinen", metric_from_key_findings(key_findings, "onderzochte_domeinen", len(domains_network)))
    col2.metric("Datastroomindicatoren", metric_from_key_findings(key_findings, "datastroom_indicatoren", len(dataflow)))
    col3.metric("Unieke leveranciers", metric_from_key_findings(key_findings, "unieke_leveranciers", supplier_summary.get("supplier", pd.Series(dtype=str)).nunique() if not supplier_summary.empty else 0))
    col4.metric("P1-vragen", metric_from_key_findings(key_findings, "p1_verificatievragen", int((questions.get("priority", pd.Series(dtype=str)) == "P1").sum()) if not questions.empty else 0))

    st.markdown("### Waarom deze kaart?")
    st.write(
        "Voor inwoners lijkt digitale dienstverlening vaak eenvoudig: je bezoekt een website, vult een formulier in of stuurt een bericht. Achter die handeling zit meestal een keten van organisaties en technieken. Denk aan mailplatformen, formulierensoftware, toegankelijkheidsdiensten, analytics, cloudplatformen, beveiligingsdiensten en websites van samenwerkingsverbanden."
    )
    st.write(
        "Dit dashboard maakt die keten zichtbaarder met informatie die publiek te vinden is. Het dashboard doet geen uitspraak dat iets fout gaat. Het laat vooral zien waar transparantie ontbreekt en welke vragen nodig zijn om de digitale keten goed te begrijpen."
    )

    with st.expander("Wat betekenen P1, P2 en P3?"):
        st.markdown(
            "- **P1**: hoogste prioriteit voor verificatie, bijvoorbeeld omdat een leverancier met niet-Europese jurisdictie wordt gecombineerd met een hoog datarisico.
"
            "- **P2**: nader onderzoeken, bijvoorbeeld omdat er een relevante leverancier of datastroom zichtbaar is, maar de urgentie lager is dan P1.
"
            "- **P3**: lagere prioriteit, maar nog steeds nuttig om te controleren voor een compleet beeld.

"
            "Deze prioriteiten zijn geen oordeel dat iets fout is. Ze helpen bepalen welke vragen als eerste aan de gemeente of leverancier gesteld moeten worden."
        )

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### Waar in de keten komen leveranciers voor?")
        st.caption("Een service layer is een laag in de digitale dienstverlening, bijvoorbeeld e-mail, scripts in de browser of hosting en netwerkdiensten.")
        if service_layers.empty:
            show_missing_file_notice("service_layer_summary", processed_dir / CSV_FILES["service_layer_summary"])
        else:
            view = compact_columns(
                service_layers,
                [
                    "service_layer",
                    "domains_count",
                    "suppliers_count",
                    "indicator_count",
                    "us_supplier_domains_count",
                    "high_data_risk_domains_count",
                    "top_suppliers",
                ],
            )
            st.dataframe(view, use_container_width=True, hide_index=True)

    with right:
        st.markdown("### Meest zichtbare leveranciers")
        st.caption("Dit zijn leveranciers of diensten die in publieke technische gegevens terugkomen. Een hoge positie betekent dat ze vaak zichtbaar zijn, niet automatisch dat ze onveilig zijn.")
        if supplier_summary.empty:
            show_missing_file_notice("supplier_summary", processed_dir / CSV_FILES["supplier_summary"])
        else:
            view = compact_columns(
                supplier_summary,
                [
                    "supplier",
                    "domains_count",
                    "highest_data_risk",
                    "p1_questions_count",
                ],
            ).head(10)
            st.dataframe(view, use_container_width=True, hide_index=True)

    st.markdown("### Domeinen die als eerste uitleg vragen")
    st.caption("Deze prioritering helpt om vervolgvragen te ordenen. P1 betekent: begin hier met verificatie, niet: hier is iets mis.")
    if domain_priority.empty:
        show_missing_file_notice("domain_priority_summary", processed_dir / CSV_FILES["domain_priority_summary"])
    else:
        view = compact_columns(
            sort_by_priority(domain_priority),
            [
                "domain",
                "priority",
                "personal_data_likelihood",
                "us_supplier_count",
                "high_risk_supplier_count",
                "p1_questions_count",
                "priority_reason",
            ],
        ).head(12)
        st.dataframe(view, use_container_width=True, hide_index=True)


# -----------------------------
# Domains
# -----------------------------

with tabs[1]:
    st.subheader("Domeinen en hun rol in de publieke keten")

    if domain_priority.empty and domains_network.empty:
        show_missing_file_notice("domain_priority_summary", processed_dir / CSV_FILES["domain_priority_summary"])
    else:
        source = domain_priority if not domain_priority.empty else domains_network

        st.write(
            "Niet elk domein is rechtstreeks eigendom van de gemeente. Sommige domeinen horen bij uitvoeringsorganisaties, samenwerkingen, leveranciers of regionale platforms. Toch kunnen inwoners deze diensten wel ervaren als onderdeel van de gemeentelijke dienstverlening."
        )
        st.write(
            "Gebruik dit overzicht om te zien welke relatie een domein heeft met de publieke keten, welke leveranciers zichtbaar zijn en welke vragen nog openstaan."
        )
        c1, c2, c3, c4 = st.columns([2, 1, 1.4, 1])
        query = c1.text_input("Zoek in domeinen", key="domain_query")
        priority_filter = c2.multiselect(
            "Prioriteit",
            options=sorted(source["priority"].dropna().unique().tolist()) if "priority" in source.columns else [],
            default=sorted(source["priority"].dropna().unique().tolist()) if "priority" in source.columns else [],
        )
        public_layer_options = sorted(source["public_service_layer"].dropna().unique().tolist()) if "public_service_layer" in source.columns else []
        public_layer_filter = c3.multiselect(
            "Rol in de publieke keten",
            options=public_layer_options,
            default=public_layer_options,
        )
        only_us = c4.checkbox("Alleen US-indicatie", value=False)

        filtered = filter_text(source, query)
        if priority_filter and "priority" in filtered.columns:
            filtered = filtered[filtered["priority"].isin(priority_filter)]
        if public_layer_filter and "public_service_layer" in filtered.columns:
            filtered = filtered[filtered["public_service_layer"].isin(public_layer_filter)]
        if only_us and "us_supplier_count" in filtered.columns:
            filtered = filtered[filtered["us_supplier_count"].fillna(0) > 0]

        filtered = sort_by_priority(filtered)
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        dataframe_download(filtered, "Download domeinenfilter", "domain_priority_filtered.csv")

        st.markdown("### Detail per domein")
        st.caption("Kies een domein om te zien welke signalen en vragen eraan gekoppeld zijn.")
        domain_options = filtered["domain"].dropna().astype(str).unique().tolist() if "domain" in filtered.columns else []
        selected_domain = st.selectbox("Kies domein", options=domain_options, index=0 if domain_options else None)

        if selected_domain:
            drow = filtered[filtered["domain"] == selected_domain]
            if not drow.empty:
                row = drow.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Prioriteit", clean(row.get("priority", "Onbekend")))
                c2.metric("US leveranciers", clean(row.get("us_supplier_count", 0)))
                c3.metric("Hoog risico leveranciers", clean(row.get("high_risk_supplier_count", 0)))
                c4.metric("P1 vragen", clean(row.get("p1_questions_count", 0)))
                st.write(clean(row.get("priority_reason", "")))

            if not dataflow.empty and "domain" in dataflow.columns:
                st.markdown("#### Datastroomindicatoren")
                st.caption(
                    "Dit zijn publieke aanwijzingen dat een domein gebruikmaakt van een leverancier of technische dienst, bijvoorbeeld via mailrecords, scripts, hostinginformatie of CDN's. "
                    "Een indicator is een startpunt voor onderzoek, geen definitief bewijs van gegevensopslag of juridische doorgifte."
                )
                st.dataframe(dataflow[dataflow["domain"] == selected_domain], use_container_width=True, hide_index=True)

            if not questions.empty and "domain" in questions.columns:
                st.markdown("#### Verificatievragen")
                st.caption(
                    "Dit zijn vragen die nodig zijn om de publieke aanwijzingen te bevestigen of te nuanceren. Denk aan vragen over datalocatie, logging, back-ups, subverwerkers en supporttoegang."
                )
                st.dataframe(sort_by_priority(questions[questions["domain"] == selected_domain]), use_container_width=True, hide_index=True)


# -----------------------------
# Suppliers
# -----------------------------

with tabs[2]:
    st.subheader("Leveranciers en diensten")
    st.write(
        "Deze tabel laat zien welke leveranciers of diensten terugkomen in publieke technische gegevens, zoals mailrecords, scripts, hostinginformatie of CDN-indicaties."
    )
    st.info(
        "Een leverancier in deze lijst betekent niet automatisch dat persoonsgegevens daar worden opgeslagen. Het betekent dat de leverancier technisch zichtbaar is en daarom mogelijk onderdeel is van de keten die verder moet worden uitgezocht."
    )

    if supplier_summary.empty:
        show_missing_file_notice("supplier_summary", processed_dir / CSV_FILES["supplier_summary"])
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        query = c1.text_input("Zoek in leveranciers", key="supplier_query")
        only_us = c2.checkbox("Alleen US-leveranciersindicatie", value=False)
        only_p1 = c3.checkbox("Alleen met P1-vragen", value=False)

        filtered = filter_text(supplier_summary, query)
        if only_us and "us_supplier_indicator" in filtered.columns:
            filtered = filtered[filtered["us_supplier_indicator"].astype(str).str.lower().isin(["true", "1", "ja"])]
        if only_p1 and "p1_questions_count" in filtered.columns:
            filtered = filtered[filtered["p1_questions_count"].fillna(0) > 0]

        st.dataframe(filtered, use_container_width=True, hide_index=True)
        dataframe_download(filtered, "Download leveranciersfilter", "supplier_summary_filtered.csv")

        st.markdown("### Detail per leverancier")
        st.caption("Bekijk bij welke domeinen een leverancier zichtbaar wordt en welke verificatievragen daarbij horen.")
        supplier_options = filtered["supplier"].dropna().astype(str).unique().tolist() if "supplier" in filtered.columns else []
        selected_supplier = st.selectbox("Kies leverancier", options=supplier_options, index=0 if supplier_options else None)

        if selected_supplier:
            detail = filtered[filtered["supplier"] == selected_supplier]
            if not detail.empty:
                row = detail.iloc[0]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Domeinen", clean(row.get("domains_count", 0)))
                c2.metric("Indicatoren", clean(row.get("indicator_count", 0)))
                c3.metric("Hoogste datarisico", clean(row.get("highest_data_risk", "")))
                c4.metric("P1-vragen", clean(row.get("p1_questions_count", 0)))
                st.write("**Type:**", clean(row.get("supplier_type", "")))
                st.write("**Jurisdictie-indicatie:**", clean(row.get("jurisdiction_groups", "")))
                st.write("**Mogelijke datacategorieën:**", clean(row.get("typical_data", "")))
                st.write("**Voorbeelddomeinen:**", clean(row.get("example_domains", "")))

            if not dataflow.empty and "supplier" in dataflow.columns:
                st.markdown("#### Datastroomindicatoren")
                st.dataframe(dataflow[dataflow["supplier"] == selected_supplier], use_container_width=True, hide_index=True)

            if not questions.empty and "supplier" in questions.columns:
                st.markdown("#### Verificatievragen")
                st.dataframe(sort_by_priority(questions[questions["supplier"] == selected_supplier]), use_container_width=True, hide_index=True)


# -----------------------------
# Dataflows
# -----------------------------

with tabs[3]:
    st.subheader("Datastroomindicatoren")
    st.write(
        "Een datastroomindicator is een publiek zichtbaar spoor van een leverancier of technische dienst. Voorbeelden zijn een mailrecord dat naar Microsoft 365 verwijst, een script van Google Tag Manager, een YouTube-insluiting, een CDN of een hostingprovider."
    )
    st.info(
        "Zie deze indicatoren als aanwijzingen voor vervolgonderzoek. Ze tonen technische betrokkenheid, maar bewijzen niet welke persoonsgegevens worden verwerkt, waar gegevens staan of welke juridische afspraken gelden."
    )

    if dataflow.empty:
        show_missing_file_notice("dataflow_matrix", processed_dir / CSV_FILES["dataflow_matrix"])
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        query = c1.text_input("Zoek in datastromen", key="dataflow_query")
        service_layers_options = sorted(dataflow["service_layer"].dropna().unique().tolist()) if "service_layer" in dataflow.columns else []
        selected_layers = c2.multiselect("Service layer", service_layers_options, default=service_layers_options)
        high_only = c3.checkbox("Alleen high risico", value=False)

        filtered = filter_text(dataflow, query)
        if selected_layers and "service_layer" in filtered.columns:
            filtered = filtered[filtered["service_layer"].isin(selected_layers)]
        if high_only and "data_risk" in filtered.columns:
            filtered = filtered[filtered["data_risk"].astype(str).str.contains("high", case=False, na=False)]

        st.dataframe(filtered, use_container_width=True, hide_index=True)
        dataframe_download(filtered, "Download datastromenfilter", "dataflow_matrix_filtered.csv")

        st.markdown("### Overzicht per ketenlaag en leverancier")
        st.caption("Deze tabel telt op hoeveel domeinen een leverancier per ketenlaag zichtbaar is.")
        if has_columns(filtered, ["service_layer", "supplier", "domain"]):
            pivot = (
                filtered.groupby(["service_layer", "supplier"])["domain"]
                .nunique()
                .reset_index(name="domains_count")
                .sort_values("domains_count", ascending=False)
            )
            st.dataframe(pivot, use_container_width=True, hide_index=True)


# -----------------------------
# Verification questions
# -----------------------------

with tabs[4]:
    st.subheader("Vragen voor verificatie")
    st.write(
        "Publieke bronnen laten niet alles zien. Ze vertellen bijvoorbeeld niet waar back-ups staan, welke supporttoegang leveranciers hebben, welke subverwerkers worden gebruikt of welke afspraken contractueel zijn vastgelegd."
    )
    st.write(
        "Deze vragen helpen om die ontbrekende context op te halen, bijvoorbeeld via gesprekken met de gemeente, leveranciers of een Woo-verzoek."
    )
    st.markdown(
        "**Prioriteiten:** **P1** betekent als eerste uitzoeken, **P2** betekent relevant vervolgonderzoek, **P3** betekent lagere prioriteit voor een compleet beeld. "
        "Een P1-vraag betekent niet dat er iets mis is. Het betekent dat de combinatie van leverancier, datarisico en publieke dienstverlening om verduidelijking vraagt."
    )

    if questions.empty:
        show_missing_file_notice("verification_questions", processed_dir / CSV_FILES["verification_questions"])
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        query = c1.text_input("Zoek in vragen", key="question_query")
        priority_options = sorted(questions["priority"].dropna().unique().tolist()) if "priority" in questions.columns else []
        selected_priorities = c2.multiselect("Prioriteit", priority_options, default=priority_options)
        supplier_options = sorted(questions["supplier"].dropna().unique().tolist()) if "supplier" in questions.columns else []
        selected_supplier = c3.selectbox("Leverancier", options=["Alle"] + supplier_options)

        filtered = filter_text(questions, query)
        if selected_priorities and "priority" in filtered.columns:
            filtered = filtered[filtered["priority"].isin(selected_priorities)]
        if selected_supplier != "Alle" and "supplier" in filtered.columns:
            filtered = filtered[filtered["supplier"] == selected_supplier]

        filtered = sort_by_priority(filtered)
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        dataframe_download(filtered, "Download verificatievragen", "verification_questions_filtered.csv")

        st.markdown("### Mogelijke selectie voor een Woo-verzoek")
        st.caption("Deze selectie kan helpen om het Woo-verzoek concreet en controleerbaar te maken.")
        p1 = filtered[filtered["priority"] == "P1"] if "priority" in filtered.columns else pd.DataFrame()
        if not p1.empty:
            st.write("Deze P1-vragen zijn geschikt als eerste Woo-bijlage of verificatielijst.")
            for _, row in p1.head(20).iterrows():
                st.markdown(
                    f"- **{clean(row.get('domain', ''))}**, {clean(row.get('supplier', ''))}: {clean(row.get('question', ''))}"
                )
        else:
            st.info("Geen P1-vragen in de huidige selectie.")


# -----------------------------
# Raw data explorer
# -----------------------------

with tabs[5]:
    st.subheader("Onderliggende data")
    st.write(
        "Dit tabblad is bedoeld voor controle en hergebruik. Hier kun je de gebruikte tabellen bekijken en downloaden."
    )

    dataset_names = [key for key, df in data.items() if not df.empty]
    if not dataset_names:
        st.info("Geen datasets gevonden.")
    else:
        selected_dataset = st.selectbox("Dataset", options=dataset_names)
        df = data[selected_dataset]
        query = st.text_input("Zoek in dataset", key="raw_data_query")
        filtered = filter_text(df, query)
        st.caption(f"{len(filtered)} van {len(df)} rijen")
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        dataframe_download(filtered, f"Download {selected_dataset}", f"{selected_dataset}.csv")

    st.markdown("### Verwachte bestanden")
    expected = []
    for key, filename in CSV_FILES.items():
        path = processed_dir / filename
        expected.append({"dataset": key, "path": str(path), "exists": path.exists()})
    for title, filename in REPORT_FILES.items():
        path = reports_dir / filename
        expected.append({"dataset": title, "path": str(path), "exists": path.exists()})
    st.dataframe(pd.DataFrame(expected), use_container_width=True, hide_index=True)
