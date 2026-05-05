"""
Streamlit prototype: Digitale footprint scanner voor gemeentelijke domeinen

Doel:
- Niet-invasief inventariseren van publieke domeinen
- DNS, mailbeveiliging, HTTPS, headers, externe scripts en hostingindicaties ophalen
- Resultaten exporteerbaar maken voor rapportage

Installatie:
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install streamlit pandas requests dnspython beautifulsoup4 tldextract

Starten:
    streamlit run app.py

Let op:
- Dit is OSINT en basiscontrole, geen pentest
- Gebruik alleen op domeinen waarvoor passieve of publieke controles passend zijn
- Internet.nl batch API vereist aparte toegang, daarom is die hier als handmatige kolom opgenomen
"""

from __future__ import annotations

import socket
import ssl
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st
import dns.resolver
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


DEFAULT_DOMAINS = """huizen.nl
www.huizen.nl
formulieren.huizen.nl
maatschappelijkezaken.nl
belastingenhbl.nl
ris.gemeenteraadhuizen.nl
sro.nl
regiogv.nl
gad.nl
vrgooienvechtstreek.nl
tomingroep.nl
dekringloper.nl
ofgv.nl
archiefgooienvechtstreek.nl
metropoolregioamsterdam.nl
bngbank.nl
randmeren.com
gnr.nl
visitgooivecht.nl
huizenduurzaam.nl
energieloketten.nl
regionaalenergieloket.nl
archiefweb.eu
readspeaker.com
"""

SECURITY_HEADERS = [
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "permissions-policy",
]

TRACKER_HINTS = [
    "google-analytics.com",
    "googletagmanager.com",
    "doubleclick.net",
    "youtube.com",
    "vimeo.com",
    "facebook.net",
    "hotjar.com",
    "matomo",
    "piwik",
    "siteimprove",
    "readspeaker",
    "simanalytics",
    "leaflet",
]


@dataclass
class ScanResult:
    checked_at: str
    domain: str
    layer: str = "Onbekend"
    relation: str = "Te verrijken"
    url: str = ""
    resolves: bool = False
    ipv4: str = ""
    ipv6: str = ""
    cname: str = ""
    nameservers: str = ""
    mx: str = ""
    spf: str = ""
    dmarc: str = ""
    https_ok: bool = False
    http_status: str = ""
    final_url: str = ""
    hsts: bool = False
    csp: bool = False
    x_frame_options: bool = False
    referrer_policy: bool = False
    permissions_policy: bool = False
    server_header: str = ""
    powered_by: str = ""
    tls_issuer: str = ""
    tls_not_after: str = ""
    security_txt: bool = False
    cookies_count: int = 0
    external_script_domains: str = ""
    tracker_hints: str = ""
    hosting_hint: str = ""
    sovereignty_hint: str = "Onbekend"
    personal_data_likelihood: str = "Te beoordelen"
    risk_score: int = 0
    risk_notes: str = ""
    error: str = ""


def normalize_domain(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"^https?://", "", value)
    value = value.split("/")[0]
    return value.strip()


def dns_query(domain: str, record_type: str) -> List[str]:
    try:
        answers = dns.resolver.resolve(domain, record_type, lifetime=5)
        return [str(r).rstrip(".") for r in answers]
    except Exception:
        return []


def get_dns(domain: str) -> Dict[str, str]:
    a = dns_query(domain, "A")
    aaaa = dns_query(domain, "AAAA")
    cname = dns_query(domain, "CNAME")
    ns = dns_query(domain, "NS")
    mx_raw = dns_query(domain, "MX")
    txt = dns_query(domain, "TXT")

    spf_records = []
    for item in txt:
        clean = item.replace('" "', '').replace('"', '')
        if clean.lower().startswith("v=spf1"):
            spf_records.append(clean)

    dmarc_records = dns_query(f"_dmarc.{domain}", "TXT")
    dmarc_clean = []
    for item in dmarc_records:
        clean = item.replace('" "', '').replace('"', '')
        if clean.lower().startswith("v=dmarc1"):
            dmarc_clean.append(clean)

    return {
        "ipv4": ", ".join(a),
        "ipv6": ", ".join(aaaa),
        "cname": ", ".join(cname),
        "nameservers": ", ".join(ns),
        "mx": ", ".join(mx_raw),
        "spf": " | ".join(spf_records),
        "dmarc": " | ".join(dmarc_clean),
    }


def get_tls_info(domain: str) -> Tuple[str, str]:
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=6) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        issuer_parts = []
        for tup in cert.get("issuer", []):
            for key, val in tup:
                if key in {"organizationName", "commonName"}:
                    issuer_parts.append(val)
        return "; ".join(issuer_parts), cert.get("notAfter", "")
    except Exception:
        return "", ""


def fetch_site(domain: str) -> Tuple[Optional[requests.Response], str]:
    url = f"https://{domain}"
    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 footprint-research/0.1"},
        )
        return response, ""
    except Exception as exc:
        return None, str(exc)


def extract_external_scripts(response: requests.Response, domain: str) -> Tuple[str, str, int]:
    content_type = response.headers.get("content-type", "")
    cookies_count = len(response.cookies)
    if "text/html" not in content_type.lower():
        return "", "", cookies_count

    soup = BeautifulSoup(response.text, "html.parser")
    script_domains = set()

    for tag in soup.find_all(["script", "iframe", "img", "link"]):
        src = tag.get("src") or tag.get("href")
        if not src:
            continue
        absolute = urljoin(response.url, src)
        parsed = urlparse(absolute)
        host = parsed.netloc.lower()
        if host and not host.endswith(domain):
            script_domains.add(host)

    hints = sorted({hint for hint in TRACKER_HINTS if hint in " ".join(script_domains).lower() or hint in response.text.lower()})
    return ", ".join(sorted(script_domains)), ", ".join(hints), cookies_count


def check_security_txt(domain: str) -> bool:
    candidates = [
        f"https://{domain}/.well-known/security.txt",
        f"https://{domain}/security.txt",
    ]
    for url in candidates:
        try:
            r = requests.get(url, timeout=5, allow_redirects=True)
            if r.status_code == 200 and "contact" in r.text.lower():
                return True
        except Exception:
            pass
    return False


def hosting_hint_from_dns(dns_data: Dict[str, str], response: Optional[requests.Response]) -> Tuple[str, str]:
    haystack = " ".join([
        dns_data.get("cname", ""),
        dns_data.get("nameservers", ""),
        response.headers.get("server", "") if response is not None else "",
    ]).lower()

    providers = {
        "azure": ("Microsoft Azure", "VS leverancier, EU-regio mogelijk, tenantgegevens nodig"),
        "cloudapp": ("Microsoft Azure", "VS leverancier, EU-regio mogelijk, tenantgegevens nodig"),
        "trafficmanager": ("Microsoft Azure", "VS leverancier, EU-regio mogelijk, tenantgegevens nodig"),
        "cloudflare": ("Cloudflare", "VS leverancier, wereldwijde edge, dataflow nader beoordelen"),
        "amazonaws": ("Amazon Web Services", "VS leverancier, regio nader bepalen"),
        "cloudfront": ("Amazon CloudFront", "VS leverancier, wereldwijde edge"),
        "google": ("Google", "VS leverancier, regio en dataflow nader bepalen"),
        "akamai": ("Akamai", "VS leverancier, wereldwijde edge"),
        "fastly": ("Fastly", "VS leverancier, wereldwijde edge"),
        "sim-cdn": ("SIMgroep CDN", "Leverancier nader beoordelen"),
        "site4u": ("Site4U", "Nederlandse hostingindicatie"),
        "transip": ("TransIP", "Nederlandse hostingindicatie"),
        "hostnet": ("Hostnet", "Nederlandse hostingindicatie"),
    }

    for key, value in providers.items():
        if key in haystack:
            return value

    return "Onbekend", "Onbekend"


def score_result(result: ScanResult) -> ScanResult:
    score = 0
    notes = []

    if not result.https_ok:
        score += 30
        notes.append("HTTPS niet bereikbaar")
    if not result.hsts:
        score += 15
        notes.append("HSTS ontbreekt")
    if not result.csp:
        score += 10
        notes.append("CSP ontbreekt")
    if not result.dmarc:
        score += 15
        notes.append("DMARC ontbreekt")
    elif "p=none" in result.dmarc.lower():
        score += 7
        notes.append("DMARC staat op none")
    if not result.spf:
        score += 10
        notes.append("SPF ontbreekt")
    if not result.security_txt:
        score += 5
        notes.append("security.txt ontbreekt")
    if result.tracker_hints:
        score += 8
        notes.append(f"Externe scripts of trackingindicaties: {result.tracker_hints}")
    if result.sovereignty_hint.startswith("VS") or "wereldwijde" in result.sovereignty_hint.lower():
        score += 12
        notes.append(f"Soevereiniteitsvraag: {result.sovereignty_hint}")
    if result.personal_data_likelihood in {"Waarschijnlijk", "Zeker"}:
        score += 10
        notes.append("Waarschijnlijk persoonsgegevens")

    result.risk_score = min(score, 100)
    result.risk_notes = "; ".join(notes)
    return result


def infer_personal_data(domain: str) -> str:
    high = ["maatschappelijkezaken", "belastingen", "formulieren"]
    medium = ["gad", "ofgv", "sro", "huizen"]
    if any(x in domain for x in high):
        return "Waarschijnlijk"
    if any(x in domain for x in medium):
        return "Mogelijk"
    return "Te beoordelen"


def infer_layer(domain: str) -> str:
    if domain.endswith("huizen.nl"):
        return "A, direct gemeentelijk"
    if domain in {"maatschappelijkezaken.nl", "belastingenhbl.nl"}:
        return "B, uitvoeringssite"
    if domain in {"regiogv.nl", "gad.nl", "vrgooienvechtstreek.nl", "tomingroep.nl", "ofgv.nl", "archiefgooienvechtstreek.nl", "sro.nl", "gnr.nl", "randmeren.com"}:
        return "C, verbonden partij of samenwerking"
    return "D, leverancier of te verifieren"


def scan_domain(domain: str) -> ScanResult:
    domain = normalize_domain(domain)
    checked_at = datetime.now(timezone.utc).isoformat()
    result = ScanResult(
        checked_at=checked_at,
        domain=domain,
        url=f"https://{domain}",
        layer=infer_layer(domain),
        personal_data_likelihood=infer_personal_data(domain),
    )

    try:
        dns_data = get_dns(domain)
        for key, value in dns_data.items():
            setattr(result, key, value)
        result.resolves = bool(result.ipv4 or result.ipv6 or result.cname)

        response, error = fetch_site(domain)
        if response is None:
            result.error = error
        else:
            result.https_ok = response.url.startswith("https://") and response.status_code < 500
            result.http_status = str(response.status_code)
            result.final_url = response.url

            headers = {k.lower(): v for k, v in response.headers.items()}
            result.hsts = "strict-transport-security" in headers
            result.csp = "content-security-policy" in headers
            result.x_frame_options = "x-frame-options" in headers
            result.referrer_policy = "referrer-policy" in headers
            result.permissions_policy = "permissions-policy" in headers
            result.server_header = headers.get("server", "")
            result.powered_by = headers.get("x-powered-by", "")

            external, hints, cookies_count = extract_external_scripts(response, domain)
            result.external_script_domains = external
            result.tracker_hints = hints
            result.cookies_count = cookies_count

        result.tls_issuer, result.tls_not_after = get_tls_info(domain)
        result.security_txt = check_security_txt(domain)
        result.hosting_hint, result.sovereignty_hint = hosting_hint_from_dns(dns_data, response)
        result = score_result(result)

    except Exception as exc:
        result.error = str(exc)

    return result


st.set_page_config(page_title="Digitale footprint scanner", layout="wide")
st.title("Digitale footprint scanner voor gemeentelijke ketens")
st.caption("Niet-invasieve OSINT voor domeinen, hostingindicaties, mailbeveiliging, headers en soevereiniteitsvragen.")

with st.sidebar:
    st.header("Instellingen")
    st.write("Plak domeinen, een per regel. Gebruik geen agressieve scans.")
    domains_text = st.text_area("Domeinen", value=DEFAULT_DOMAINS, height=360)
    run = st.button("Start scan", type="primary")
    st.divider()
    st.markdown("**Interpretatie**")
    st.markdown("Een hoge score betekent niet automatisch een kwetsbaarheid. Het betekent: prioriteit voor nader onderzoek.")

if not run:
    st.info("Klik op 'Start scan' om de publieke controles uit te voeren.")
    st.stop()

raw_domains = [normalize_domain(x) for x in domains_text.splitlines() if normalize_domain(x)]
domains = list(dict.fromkeys(raw_domains))

progress = st.progress(0)
results: List[ScanResult] = []

for idx, domain in enumerate(domains, start=1):
    st.write(f"Scannen: {domain}")
    results.append(scan_domain(domain))
    progress.progress(idx / len(domains))

rows = [asdict(r) for r in results]
df = pd.DataFrame(rows)

st.subheader("Resultaten")
st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", data=csv, file_name="digitale_footprint_huizen.csv", mime="text/csv")

json_data = json.dumps(rows, ensure_ascii=False, indent=2).encode("utf-8")
st.download_button("Download JSON", data=json_data, file_name="digitale_footprint_huizen.json", mime="application/json")

st.subheader("Prioriteiten")
priority_cols = [
    "domain",
    "layer",
    "personal_data_likelihood",
    "risk_score",
    "hosting_hint",
    "sovereignty_hint",
    "risk_notes",
]
st.dataframe(df[priority_cols].sort_values("risk_score", ascending=False), use_container_width=True)

st.subheader("Samenvatting")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Domeinen", len(df))
col2.metric("HTTPS ok", int(df["https_ok"].sum()))
col3.metric("HSTS", int(df["hsts"].sum()))
col4.metric("DMARC", int(df["dmarc"].astype(bool).sum()))

st.warning(
    "Hostingland en jurisdictie zijn indicaties. Voor zekerheid zijn contracten, subverwerkerslijsten, tenantinstellingen en gemeentelijke documentatie nodig."
)
