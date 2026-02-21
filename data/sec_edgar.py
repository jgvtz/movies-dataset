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


@st.cache_data(ttl=3600, show_spinner="Parsing 13F information table...")
def parse_13f_xml(cik: str, accession: str) -> pd.DataFrame:
    """Parse the 13F information table XML for a specific filing."""
    cik_clean = cik.lstrip("0")
    acc_no_dashes = accession.replace("-", "")

    # First, get the filing index to find the XML info table file
    index_url = f"{SEC_ARCHIVES}/{cik_clean}/{acc_no_dashes}/"
    _rate_limit()
    resp = requests.get(index_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    # Look for the infotable XML file in the index
    xml_filename = None
    for line in resp.text.split("\n"):
        lower = line.lower()
        if "infotable" in lower and ".xml" in lower:
            # Extract filename from the HTML
            import re
            match = re.search(r'href="([^"]*infotable[^"]*\.xml)"', lower)
            if match:
                xml_filename = match.group(1)
                break

    if not xml_filename:
        # Try alternate pattern - look for any XML that's not the primary doc
        for line in resp.text.split("\n"):
            if ".xml" in line.lower() and "primary_doc" not in line.lower():
                import re
                match = re.search(r'href="([^"]*\.xml)"', line.lower())
                if match:
                    xml_filename = match.group(1)
                    break

    if not xml_filename:
        return pd.DataFrame()

    # Fetch and parse the XML
    xml_url = f"{SEC_ARCHIVES}/{cik_clean}/{acc_no_dashes}/{xml_filename}"
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
