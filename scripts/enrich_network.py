"""
scripts/enrich_network.py

Verrijkt domains_enriched.csv met netwerk- en hostinginformatie.

Doel:
- IP-adressen uit de scan normaliseren
- ASN, ASN-naam en land ophalen via publieke RDAP API's
- Cloud/CDN/hosting-indicaties afleiden uit CNAME, nameservers, server headers en ASN
- Soevereiniteitsduiding toevoegen
- Output schrijven naar data/processed/latest/domains_network_enriched.csv

Installatie:
    pip install pandas requests

Gebruik:
    python scripts/enrich_network.py \
      --input data/processed/latest/domains_enriched.csv \
      --output data/processed/latest/domains_network_enriched.csv

Let op:
- Dit is geen pentest en doet geen actieve kwetsbaarheidsscan.
- RDAP en IP-geolocatie zijn indicatief.
- CDN's kunnen land en hosting maskeren.
- Juridische datalocatie is niet gelijk aan IP-locatie.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import requests


RDAP_BOOTSTRAP_URL = "https://data.iana.org/rdap/ipv4.json"
REQUEST_TIMEOUT = 12
SLEEP_SECONDS = 0.15


@dataclass
class NetworkIntel:
    domain: str
    primary_ip: str = ""
    ip_version: str = ""
    rdap_name: str = ""
    rdap_country: str = ""
    rdap_handle: str = ""
    rdap_parent_handle: str = ""
    asn_hint: str = ""
    network_provider_hint: str = ""
    cloud_or_cdn_hint: str = ""
    network_jurisdiction_hint: str = "Onbekend"
    network_confidence: str = "Laag"
    network_notes: str = ""


def first_non_empty(*values: object) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text and text.lower() != "nan":
            return text
    return ""


def split_csvish(value: object) -> List[str]:
    text = first_non_empty(value)
    if not text:
        return []
    parts = re.split(r"[,;|\s]+", text)
    return [p.strip() for p in parts if p.strip()]


def extract_ips(row: pd.Series) -> List[str]:
    ips: List[str] = []
    for col in ["ipv4", "ip", "a_record", "ipv6", "aaaa_record"]:
        if col in row.index:
            for item in split_csvish(row.get(col, "")):
                clean = item.strip("[]()")
                try:
                    ipaddress.ip_address(clean)
                    ips.append(clean)
                except ValueError:
                    pass
    return list(dict.fromkeys(ips))


def load_rdap_bootstrap() -> List[Tuple[ipaddress.IPv4Network, str]]:
    """Load IANA RDAP bootstrap ranges for IPv4.

    Returns a list of network ranges with their RDAP base URL.
    """
    response = requests.get(RDAP_BOOTSTRAP_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    ranges: List[Tuple[ipaddress.IPv4Network, str]] = []
    for service in data.get("services", []):
        cidrs, urls = service
        if not urls:
            continue
        base_url = urls[0].rstrip("/")
        for cidr in cidrs:
            try:
                ranges.append((ipaddress.ip_network(cidr), base_url))
            except ValueError:
                continue
    return ranges


def rdap_base_for_ip(ip: str, bootstrap: List[Tuple[ipaddress.IPv4Network, str]]) -> Optional[str]:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    if addr.version != 4:
        return None
    for network, base_url in bootstrap:
        if addr in network:
            return base_url
    return None


def fetch_rdap(ip: str, bootstrap: List[Tuple[ipaddress.IPv4Network, str]], cache: Dict[str, Dict]) -> Dict:
    if ip in cache:
        return cache[ip]

    base_url = rdap_base_for_ip(ip, bootstrap)
    if not base_url:
        cache[ip] = {}
        return {}

    url = f"{base_url}/ip/{ip}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "digitale-ketenkaart/0.2"})
        if response.status_code == 200:
            cache[ip] = response.json()
        else:
            cache[ip] = {"error": f"HTTP {response.status_code}"}
    except Exception as exc:
        cache[ip] = {"error": str(exc)}

    time.sleep(SLEEP_SECONDS)
    return cache[ip]


def rdap_text(data: Dict) -> str:
    parts = []
    for key in ["name", "handle", "country", "parentHandle", "type"]:
        value = data.get(key)
        if value:
            parts.append(str(value))
    for event in data.get("events", []) or []:
        parts.append(str(event.get("eventAction", "")))
    for entity in data.get("entities", []) or []:
        parts.append(str(entity.get("handle", "")))
        for vcard in entity.get("vcardArray", [None, []])[1] if entity.get("vcardArray") else []:
            if isinstance(vcard, list) and len(vcard) >= 4:
                parts.append(str(vcard[3]))
    return " ".join(parts).lower()


def infer_provider(row: pd.Series, rdap: Dict) -> Tuple[str, str, str, str, str]:
    """Return provider, cloud/cdn, jurisdiction, confidence, notes."""
    haystack = " ".join(
        [
            first_non_empty(row.get("domain", "")),
            first_non_empty(row.get("cname", "")),
            first_non_empty(row.get("nameservers", "")),
            first_non_empty(row.get("server_header", "")),
            first_non_empty(row.get("hosting_hint", "")),
            first_non_empty(row.get("sovereignty_hint", "")),
            first_non_empty(row.get("external_script_domains", "")),
            rdap_text(rdap),
        ]
    ).lower()

    rules = [
        ("cloudflare", "Cloudflare", "CDN/WAF", "VS leverancier, wereldwijde edge", "Hoog"),
        ("akamai", "Akamai", "CDN/WAF", "VS leverancier, wereldwijde edge", "Hoog"),
        ("cloudfront", "Amazon CloudFront", "CDN", "VS leverancier, wereldwijde edge", "Hoog"),
        ("amazonaws", "Amazon Web Services", "Cloud", "VS leverancier, regio contractueel verifieren", "Hoog"),
        ("aws", "Amazon Web Services", "Cloud", "VS leverancier, regio contractueel verifieren", "Middel"),
        ("azure", "Microsoft Azure", "Cloud", "VS leverancier, EU-regio mogelijk, tenantgegevens nodig", "Hoog"),
        ("microsoft", "Microsoft", "Cloud/SaaS", "VS leverancier, EU-regio mogelijk, tenantgegevens nodig", "Middel"),
        ("google", "Google", "Cloud/SaaS", "VS leverancier, regio en dataflow verifieren", "Middel"),
        ("fastly", "Fastly", "CDN/WAF", "VS leverancier, wereldwijde edge", "Hoog"),
        ("sim-cdn", "SIMgroep CDN", "Gemeentelijke webleverancier", "Nederlandse leverancier, hostingketen verifieren", "Middel"),
        ("simgroep", "SIMgroep", "Gemeentelijke webleverancier", "Nederlandse leverancier, hostingketen verifieren", "Middel"),
        ("transip", "TransIP", "Hosting", "Nederlandse hostingindicatie", "Hoog"),
        ("team.blue", "team.blue", "Hosting", "Europese hostinggroep, locatie verifieren", "Middel"),
        ("hostnet", "Hostnet", "Hosting", "Nederlandse hostingindicatie", "Hoog"),
        ("leaseweb", "Leaseweb", "Hosting", "Nederlandse hostingindicatie, internationale footprint mogelijk", "Hoog"),
        ("sentia", "Sentia", "Hosting/Cloud", "Europese hostingindicatie, locatie verifieren", "Middel"),
        ("true", "True", "Hosting/Cloud", "Nederlandse hostingindicatie", "Laag"),
        ("pink", "Pink", "Cloud/hosting", "Nederlandse of Europese cloudindicatie, contractueel verifieren", "Middel"),
    ]

    hits = []
    for needle, provider, kind, jurisdiction, confidence in rules:
        if needle in haystack:
            hits.append((provider, kind, jurisdiction, confidence))

    if not hits:
        return "Onbekend", "Onbekend", "Onbekend", "Laag", "Geen providerregel geraakt"

    providers = sorted(set(h[0] for h in hits))
    kinds = sorted(set(h[1] for h in hits))
    jurisdictions = sorted(set(h[2] for h in hits))
    confidences = [h[3] for h in hits]
    confidence = "Hoog" if "Hoog" in confidences else "Middel" if "Middel" in confidences else "Laag"
    notes = "Afgeleid uit DNS, headers, bestaande hosting_hint en RDAP. Handmatig verifieren bij CDN of SaaS."
    return ", ".join(providers), ", ".join(kinds), " | ".join(jurisdictions), confidence, notes


def enrich(input_path: Path, output_path: Path, cache_path: Optional[Path] = None) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    if "domain" not in df.columns:
        raise ValueError("Input CSV moet een kolom 'domain' bevatten")

    cache: Dict[str, Dict] = {}
    if cache_path and cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))

    bootstrap = load_rdap_bootstrap()
    results: List[NetworkIntel] = []

    for _, row in df.iterrows():
        domain = first_non_empty(row.get("domain", ""))
        ips = extract_ips(row)
        primary_ip = ips[0] if ips else ""
        intel = NetworkIntel(domain=domain, primary_ip=primary_ip)

        if primary_ip:
            try:
                ip_obj = ipaddress.ip_address(primary_ip)
                intel.ip_version = f"IPv{ip_obj.version}"
            except ValueError:
                pass

            rdap = fetch_rdap(primary_ip, bootstrap, cache)
            intel.rdap_name = first_non_empty(rdap.get("name", ""))
            intel.rdap_country = first_non_empty(rdap.get("country", ""))
            intel.rdap_handle = first_non_empty(rdap.get("handle", ""))
            intel.rdap_parent_handle = first_non_empty(rdap.get("parentHandle", ""))
        else:
            rdap = {}
            intel.network_notes = "Geen IP-adres in input gevonden"

        provider, kind, jurisdiction, confidence, notes = infer_provider(row, rdap)
        intel.network_provider_hint = provider
        intel.cloud_or_cdn_hint = kind
        intel.network_jurisdiction_hint = jurisdiction
        intel.network_confidence = confidence
        intel.network_notes = "; ".join([x for x in [intel.network_notes, notes] if x])

        results.append(intel)

    network_df = pd.DataFrame([asdict(r) for r in results])
    merged = df.merge(network_df, on="domain", how="left")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)

    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="Verrijk domeinen met netwerk- en hostinginformatie")
    parser.add_argument("--input", default="data/processed/latest/domains_enriched.csv")
    parser.add_argument("--output", default="data/processed/latest/domains_network_enriched.csv")
    parser.add_argument("--cache", default="data/processed/latest/rdap_cache.json")
    args = parser.parse_args()

    output = enrich(Path(args.input), Path(args.output), Path(args.cache))
    print(f"[OK] wrote {args.output} with {len(output)} rows")


if __name__ == "__main__":
    main()
