"""
SEC EDGAR 13F Live Data Fetcher
================================
Fetches 13F filing data directly from SEC EDGAR (public API).

This module will work when deployed on Streamlit Cloud or any
environment with full internet access. SEC EDGAR requires a
User-Agent header with contact info for API access.

Usage:
    from data.sec_edgar import fetch_fund_holdings
    df = fetch_fund_holdings("0001647251", num_quarters=4)
"""

import re
import time
import xml.etree.ElementTree as ET

import pandas as pd
import requests
import streamlit as st

SEC_BASE = "https://data.sec.gov"
SEC_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
HEADERS = {
    "User-Agent": "13FundTracker admin@13ftracker.app",
    "Accept-Encoding": "gzip, deflate",
}

# Map of fund names to CIK numbers
FUND_CIKS = {
    "TCI Fund Management": "0001647251",
    "Egerton Capital": "0001535392",
    "AKO Capital": "0001606058",
    "ValueAct Capital": "0001418814",
    "Lone Pine Capital": "0001061768",
}

# 13F XML namespace
NS = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

# Common info table filenames used by SEC filers
COMMON_INFOTABLE_NAMES = [
    "Form13fInfoTable.xml",
    "form13fInfoTable.xml",
    "form13finfoTable.xml",
    "infotable.xml",
    "InfoTable.xml",
    "INFOTABLE.XML",
]


def _rate_limit():
    """SEC EDGAR allows max 10 requests/second."""
    time.sleep(0.15)


def _get(url: str) -> requests.Response:
    """Make a rate-limited GET request to SEC EDGAR."""
    _rate_limit()
    return requests.get(url, headers=HEADERS, timeout=20)


@st.cache_data(ttl=3600, show_spinner="Fetching filings from SEC EDGAR...")
def get_recent_13f_filings(cik: str, num_filings: int = 4) -> list[dict]:
    """Get the most recent 13F-HR filing accession numbers for a CIK."""
    cik_padded = cik.zfill(10)
    url = f"{SEC_BASE}/submissions/CIK{cik_padded}.json"

    resp = _get(url)
    resp.raise_for_status()
    data = resp.json()

    filings = []
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])

    for i, form in enumerate(forms):
        if form in ("13F-HR", "13F-HR/A") and len(filings) < num_filings:
            filings.append({
                "accession": accessions[i],
                "filing_date": dates[i],
                "report_date": report_dates[i],
                "form": form,
            })

    return filings


def _find_info_table_url(cik: str, accession: str) -> str | None:
    """Find the info table XML URL for a 13F filing using multiple strategies.

    Returns the full URL to the info table XML, or None if not found.
    """
    cik_clean = cik.lstrip("0")
    acc_no_dashes = accession.replace("-", "")
    base_url = f"{SEC_ARCHIVES}/{cik_clean}/{acc_no_dashes}"

    # ── Strategy 1: JSON filing index (most reliable, exact filenames) ──
    try:
        resp = _get(f"{base_url}/index.json")
        if resp.status_code == 200:
            items = resp.json().get("directory", {}).get("item", [])
            for item in items:
                name = item.get("name", "")
                if re.search(r'info.*table', name, re.IGNORECASE) and name.lower().endswith(".xml"):
                    return f"{base_url}/{name}"
    except Exception:
        pass

    # ── Strategy 2: HTML directory scraping (proven approach from 13f.info) ──
    try:
        resp = _get(base_url)
        if resp.status_code == 200:
            # Extract all .xml hrefs, preserving original case
            hrefs = re.findall(r'href="([^"]+\.xml)"', resp.text, re.IGNORECASE)
            xml_urls = []
            for h in hrefs:
                if h.startswith("http"):
                    xml_urls.append(h)
                elif h.startswith("/"):
                    xml_urls.append(f"https://www.sec.gov{h}")
                else:
                    xml_urls.append(f"{base_url}/{h}")

            # 2a: Match by URL pattern
            for url in xml_urls:
                if re.search(r'info.*table', url, re.IGNORECASE):
                    return url

            # 2b: Download each XML and check for <informationTable> root
            for url in xml_urls:
                try:
                    r = _get(url)
                    if r.status_code != 200:
                        continue
                    root = ET.fromstring(r.content)
                    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
                    if tag.lower() == "informationtable":
                        return url
                except Exception:
                    continue
    except Exception:
        pass

    # ── Strategy 3: Try common filenames directly ──
    for name in COMMON_INFOTABLE_NAMES:
        try:
            url = f"{base_url}/{name}"
            r = _get(url)
            if r.status_code == 200 and b"<" in r.content[:100]:
                return url
        except Exception:
            continue

    return None


@st.cache_data(ttl=3600, show_spinner="Parsing 13F information table...")
def parse_13f_xml(cik: str, accession: str) -> pd.DataFrame:
    """Parse the 13F information table XML for a specific filing."""
    xml_url = _find_info_table_url(cik, accession)
    if not xml_url:
        raise ValueError(f"Could not find info table XML for CIK={cik} accession={accession}")

    resp = _get(xml_url)
    resp.raise_for_status()

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML from {xml_url}: {e}")

    holdings = []
    # Try with namespace
    info_tables = root.findall(".//ns:infoTable", NS)
    if not info_tables:
        # Try without namespace
        info_tables = root.findall(".//{http://www.sec.gov/edgar/document/thirteenf/informationtable}infoTable")
    if not info_tables:
        # Try plain tags
        info_tables = root.findall(".//infoTable")

    for entry in info_tables:
        def _get_tag(tag):
            for prefix in [
                f"{{{NS['ns']}}}",
                "{http://www.sec.gov/edgar/document/thirteenf/informationtable}",
                "",
            ]:
                el = entry.find(f"{prefix}{tag}")
                if el is not None and el.text:
                    return el.text.strip()
            return ""

        def _get_nested(parent_tag, child_tag):
            for prefix in [
                f"{{{NS['ns']}}}",
                "{http://www.sec.gov/edgar/document/thirteenf/informationtable}",
                "",
            ]:
                parent = entry.find(f"{prefix}{parent_tag}")
                if parent is not None:
                    child = parent.find(f"{prefix}{child_tag}")
                    if child is not None and child.text:
                        return child.text.strip()
            return ""

        value_str = _get_tag("value")
        shares_str = _get_nested("shrsOrPrnAmt", "sshPrnamt")

        holdings.append({
            "company": _get_tag("nameOfIssuer"),
            "cusip": _get_tag("cusip"),
            "value_usd": int(value_str) * 1000 if value_str else 0,  # 13F reports in thousands
            "shares": int(shares_str) if shares_str else 0,
            "share_type": _get_nested("shrsOrPrnAmt", "sshPrnamtType"),
            "investment_discretion": _get_tag("investmentDiscretion"),
        })

    return pd.DataFrame(holdings)


@st.cache_data(ttl=3600, show_spinner="Fetching fund 13F data...")
def fetch_fund_holdings(
    fund_name: str,
    cik: str,
    num_quarters: int = 2,
) -> pd.DataFrame:
    """Fetch and combine multiple quarters of 13F data for a fund."""
    filings = get_recent_13f_filings(cik, num_quarters)
    all_dfs = []
    errors = []

    for filing in filings:
        try:
            df = parse_13f_xml(cik, filing["accession"])
        except Exception as e:
            errors.append(f"{fund_name} {filing['accession']}: {e}")
            continue
        if df.empty:
            continue
        df["fund"] = fund_name
        df["report_date"] = filing["report_date"]
        df["filing_date"] = filing["filing_date"]

        # Compute quarter label
        rd = pd.Timestamp(filing["report_date"])
        q = (rd.month - 1) // 3 + 1
        df["quarter"] = f"Q{q} {rd.year}"

        # Compute portfolio weight
        total_val = df["value_usd"].sum()
        df["pct_portfolio"] = (df["value_usd"] / total_val * 100).round(2) if total_val > 0 else 0

        all_dfs.append(df)

    if errors:
        for err in errors:
            st.warning(err)

    if not all_dfs:
        return pd.DataFrame()

    combined = pd.concat(all_dfs, ignore_index=True)
    combined["value_bn"] = combined["value_usd"] / 1e9
    combined["value_mn"] = combined["value_usd"] / 1e6
    return combined


def fetch_all_funds(num_quarters: int = 2) -> pd.DataFrame:
    """Fetch 13F data for all tracked funds."""
    all_dfs = []
    for fund_name, cik in FUND_CIKS.items():
        try:
            df = fetch_fund_holdings(fund_name, cik, num_quarters)
            if not df.empty:
                all_dfs.append(df)
        except Exception as e:
            st.warning(f"Could not fetch data for {fund_name}: {e}")
            continue

    if not all_dfs:
        return pd.DataFrame()

    return pd.concat(all_dfs, ignore_index=True)
