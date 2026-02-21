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


def _rate_limit():
    """SEC EDGAR allows max 10 requests/second."""
    time.sleep(0.12)


@st.cache_data(ttl=3600, show_spinner="Fetching filings from SEC EDGAR...")
def get_recent_13f_filings(cik: str, num_filings: int = 4) -> list[dict]:
    """Get the most recent 13F-HR filing accession numbers for a CIK."""
    cik_padded = cik.zfill(10)
    url = f"{SEC_BASE}/submissions/CIK{cik_padded}.json"

    _rate_limit()
    resp = requests.get(url, headers=HEADERS, timeout=15)
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


def _resolve_xml_url(href: str) -> str:
    """Resolve an href from an EDGAR filing index page to a full URL."""
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return f"https://www.sec.gov{href}"
    return f"https://www.sec.gov/{href}"


def _collect_xml_urls(directory_url: str) -> list[str]:
    """Fetch the EDGAR filing directory and return all XML document URLs.

    Mirrors the approach used by github.com/toddwschneider/sec-13f-filings:
    fetch the directory HTML, find all <a> links ending in .xml.
    """
    import re

    _rate_limit()
    resp = requests.get(directory_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    # Extract all href values pointing to .xml files (preserve original case)
    hrefs = re.findall(r'href="([^"]+\.xml)"', resp.text, re.IGNORECASE)
    return [_resolve_xml_url(h) for h in hrefs]


def _find_info_table_url(xml_urls: list[str]) -> str | None:
    """Identify the info table XML from a list of filing XML URLs.

    Strategy 1: regex match for 'info.*table' in the URL (covers most filings).
    Strategy 2: download each XML and check for <informationTable> element.
    """
    import re

    # Strategy 1: Match URL pattern (fast, no extra downloads)
    for url in xml_urls:
        if re.search(r'info.*table', url, re.IGNORECASE):
            return url

    # Strategy 2: Download each XML and inspect content (robust fallback)
    for url in xml_urls:
        try:
            _rate_limit()
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                continue
            root = ET.fromstring(resp.content)
            # Strip namespaces for simpler matching
            tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
            if tag.lower() == "informationtable":
                return url
        except Exception:
            continue

    return None


@st.cache_data(ttl=3600, show_spinner="Parsing 13F information table...")
def parse_13f_xml(cik: str, accession: str) -> pd.DataFrame:
    """Parse the 13F information table XML for a specific filing."""
    cik_clean = cik.lstrip("0")
    acc_no_dashes = accession.replace("-", "")
    directory_url = f"{SEC_ARCHIVES}/{cik_clean}/{acc_no_dashes}"

    # Collect all XML URLs from the filing directory page
    xml_urls = _collect_xml_urls(directory_url)
    if not xml_urls:
        return pd.DataFrame()

    # Find the info table XML
    xml_url = _find_info_table_url(xml_urls)
    if not xml_url:
        return pd.DataFrame()

    _rate_limit()
    resp = requests.get(xml_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        return pd.DataFrame()

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
        def _get(tag):
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

        value_str = _get("value")
        shares_str = _get_nested("shrsOrPrnAmt", "sshPrnamt")

        holdings.append({
            "company": _get("nameOfIssuer"),
            "cusip": _get("cusip"),
            "value_usd": int(value_str) * 1000 if value_str else 0,  # 13F reports in thousands
            "shares": int(shares_str) if shares_str else 0,
            "share_type": _get_nested("shrsOrPrnAmt", "sshPrnamtType"),
            "investment_discretion": _get("investmentDiscretion"),
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

    for filing in filings:
        df = parse_13f_xml(cik, filing["accession"])
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
