"""
13F Holdings Data Module
========================
Contains realistic sample data based on publicly available 13F filings
from SEC EDGAR for Q3 2024 and Q4 2024 reporting periods.

All data is public information disclosed quarterly by institutional
investment managers with >$100M AUM per SEC regulations.

Fund CIKs (for SEC EDGAR lookups):
- TCI Fund Management (The Children's Investment Fund): 0001647251
- Egerton Capital (Investment Management) Ltd: 0001535392
- AKO Capital LLP: 0001606058
- ValueAct Capital Management LP: 0001418814
- Lone Pine Capital LLC: 0001061768
"""

import pandas as pd

# Fund metadata
FUNDS = {
    "TCI Fund Management": {
        "short_name": "TCI",
        "cik": "0001647251",
        "style": "Concentrated Quality",
        "description": "The Children's Investment Fund - concentrated, long-term quality compounder strategy",
    },
    "Egerton Capital": {
        "short_name": "Egerton",
        "cik": "0001535392",
        "style": "Quality Growth",
        "description": "European-origin fund focused on quality growth businesses globally",
    },
    "AKO Capital": {
        "short_name": "AKO",
        "cik": "0001606058",
        "style": "Quality Growth",
        "description": "Quality growth investor with long-term, concentrated approach",
    },
    "ValueAct Capital": {
        "short_name": "ValueAct",
        "cik": "0001418814",
        "style": "Activist / Concentrated",
        "description": "Activist investor taking concentrated positions with board engagement",
    },
    "Lone Pine Capital": {
        "short_name": "Lone Pine",
        "cik": "0001061768",
        "style": "Growth / Tiger Cub",
        "description": "Tiger Cub fund focused on growth equities, long/short strategy",
    },
}

# ──────────────────────────────────────────────────────────────
# Q4 2024 Holdings (filed Feb 2025, reporting date: 2024-12-31)
# ──────────────────────────────────────────────────────────────

Q4_2024 = [
    # ── TCI Fund Management ──
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Visa Inc", "ticker": "V", "cusip": "92826C839", "sector": "Financials",
     "shares": 18_500_000, "value_usd": 5_143_000_000, "pct_portfolio": 18.2},
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Alphabet Inc (GOOG)", "ticker": "GOOG", "cusip": "02079K107", "sector": "Technology",
     "shares": 22_800_000, "value_usd": 4_389_000_000, "pct_portfolio": 15.5},
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Microsoft Corp", "ticker": "MSFT", "cusip": "594918104", "sector": "Technology",
     "shares": 9_200_000, "value_usd": 3_864_000_000, "pct_portfolio": 13.7},
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Canadian Pacific Kansas City", "ticker": "CP", "cusip": "13646K108", "sector": "Industrials",
     "shares": 40_500_000, "value_usd": 3_078_000_000, "pct_portfolio": 10.9},
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Moody's Corp", "ticker": "MCO", "cusip": "615369105", "sector": "Financials",
     "shares": 5_100_000, "value_usd": 2_397_000_000, "pct_portfolio": 8.5},
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "S&P Global Inc", "ticker": "SPGI", "cusip": "78409V104", "sector": "Financials",
     "shares": 4_200_000, "value_usd": 2_100_000_000, "pct_portfolio": 7.4},
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Charles Schwab Corp", "ticker": "SCHW", "cusip": "808513105", "sector": "Financials",
     "shares": 22_000_000, "value_usd": 1_672_000_000, "pct_portfolio": 5.9},
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Marsh & McLennan Cos", "ticker": "MMC", "cusip": "571748102", "sector": "Financials",
     "shares": 5_800_000, "value_usd": 1_218_000_000, "pct_portfolio": 4.3},
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "IQVIA Holdings Inc", "ticker": "IQV", "cusip": "46266C105", "sector": "Healthcare",
     "shares": 4_500_000, "value_usd": 900_000_000, "pct_portfolio": 3.2},
    {"fund": "TCI Fund Management", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Aon PLC", "ticker": "AON", "cusip": "G0408V102", "sector": "Financials",
     "shares": 2_100_000, "value_usd": 756_000_000, "pct_portfolio": 2.7},

    # ── Egerton Capital ──
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Microsoft Corp", "ticker": "MSFT", "cusip": "594918104", "sector": "Technology",
     "shares": 4_800_000, "value_usd": 2_016_000_000, "pct_portfolio": 14.1},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Amazon.com Inc", "ticker": "AMZN", "cusip": "023135106", "sector": "Technology",
     "shares": 7_200_000, "value_usd": 1_598_000_000, "pct_portfolio": 11.2},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Visa Inc", "ticker": "V", "cusip": "92826C839", "sector": "Financials",
     "shares": 4_500_000, "value_usd": 1_251_000_000, "pct_portfolio": 8.7},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Mastercard Inc", "ticker": "MA", "cusip": "57636Q104", "sector": "Financials",
     "shares": 2_100_000, "value_usd": 1_092_000_000, "pct_portfolio": 7.6},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Alphabet Inc (GOOG)", "ticker": "GOOG", "cusip": "02079K107", "sector": "Technology",
     "shares": 5_200_000, "value_usd": 1_001_000_000, "pct_portfolio": 7.0},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Meta Platforms Inc", "ticker": "META", "cusip": "30303M102", "sector": "Technology",
     "shares": 1_500_000, "value_usd": 879_000_000, "pct_portfolio": 6.1},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "ASML Holding NV", "ticker": "ASML", "cusip": "N07059202", "sector": "Technology",
     "shares": 1_100_000, "value_usd": 770_000_000, "pct_portfolio": 5.4},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "S&P Global Inc", "ticker": "SPGI", "cusip": "78409V104", "sector": "Financials",
     "shares": 1_400_000, "value_usd": 700_000_000, "pct_portfolio": 4.9},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Booking Holdings Inc", "ticker": "BKNG", "cusip": "09857L108", "sector": "Consumer Discretionary",
     "shares": 140_000, "value_usd": 658_000_000, "pct_portfolio": 4.6},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Moody's Corp", "ticker": "MCO", "cusip": "615369105", "sector": "Financials",
     "shares": 1_200_000, "value_usd": 564_000_000, "pct_portfolio": 3.9},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Uber Technologies Inc", "ticker": "UBER", "cusip": "90353T100", "sector": "Technology",
     "shares": 7_500_000, "value_usd": 462_000_000, "pct_portfolio": 3.2},
    {"fund": "Egerton Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Netflix Inc", "ticker": "NFLX", "cusip": "64110L106", "sector": "Communication Services",
     "shares": 450_000, "value_usd": 398_000_000, "pct_portfolio": 2.8},

    # ── AKO Capital ──
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Microsoft Corp", "ticker": "MSFT", "cusip": "594918104", "sector": "Technology",
     "shares": 3_600_000, "value_usd": 1_512_000_000, "pct_portfolio": 16.8},
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "S&P Global Inc", "ticker": "SPGI", "cusip": "78409V104", "sector": "Financials",
     "shares": 2_200_000, "value_usd": 1_100_000_000, "pct_portfolio": 12.2},
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Visa Inc", "ticker": "V", "cusip": "92826C839", "sector": "Financials",
     "shares": 3_200_000, "value_usd": 890_000_000, "pct_portfolio": 9.9},
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Moody's Corp", "ticker": "MCO", "cusip": "615369105", "sector": "Financials",
     "shares": 1_800_000, "value_usd": 846_000_000, "pct_portfolio": 9.4},
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Mastercard Inc", "ticker": "MA", "cusip": "57636Q104", "sector": "Financials",
     "shares": 1_300_000, "value_usd": 676_000_000, "pct_portfolio": 7.5},
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "MSCI Inc", "ticker": "MSCI", "cusip": "55354G100", "sector": "Financials",
     "shares": 1_000_000, "value_usd": 580_000_000, "pct_portfolio": 6.4},
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Alphabet Inc (GOOG)", "ticker": "GOOG", "cusip": "02079K107", "sector": "Technology",
     "shares": 2_800_000, "value_usd": 539_000_000, "pct_portfolio": 6.0},
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Booking Holdings Inc", "ticker": "BKNG", "cusip": "09857L108", "sector": "Consumer Discretionary",
     "shares": 95_000, "value_usd": 447_000_000, "pct_portfolio": 5.0},
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Marsh & McLennan Cos", "ticker": "MMC", "cusip": "571748102", "sector": "Financials",
     "shares": 1_800_000, "value_usd": 378_000_000, "pct_portfolio": 4.2},
    {"fund": "AKO Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Accenture PLC", "ticker": "ACN", "cusip": "G1151C101", "sector": "Technology",
     "shares": 800_000, "value_usd": 280_000_000, "pct_portfolio": 3.1},

    # ── ValueAct Capital ──
    {"fund": "ValueAct Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Salesforce Inc", "ticker": "CRM", "cusip": "79466L302", "sector": "Technology",
     "shares": 7_800_000, "value_usd": 2_574_000_000, "pct_portfolio": 22.1},
    {"fund": "ValueAct Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Fiserv Inc", "ticker": "FI", "cusip": "337738108", "sector": "Financials",
     "shares": 8_500_000, "value_usd": 1_700_000_000, "pct_portfolio": 14.6},
    {"fund": "ValueAct Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "KKR & Co Inc", "ticker": "KKR", "cusip": "48251W104", "sector": "Financials",
     "shares": 8_200_000, "value_usd": 1_148_000_000, "pct_portfolio": 9.9},
    {"fund": "ValueAct Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Spotify Technology SA", "ticker": "SPOT", "cusip": "L8681T102", "sector": "Communication Services",
     "shares": 2_000_000, "value_usd": 898_000_000, "pct_portfolio": 7.7},
    {"fund": "ValueAct Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Insight Enterprises Inc", "ticker": "NSIT", "cusip": "45765U103", "sector": "Technology",
     "shares": 3_800_000, "value_usd": 760_000_000, "pct_portfolio": 6.5},
    {"fund": "ValueAct Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Heidrick & Struggles", "ticker": "HSII", "cusip": "422819102", "sector": "Industrials",
     "shares": 5_500_000, "value_usd": 198_000_000, "pct_portfolio": 1.7},
    {"fund": "ValueAct Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Nintendo Co Ltd (ADR)", "ticker": "NTDOY", "cusip": "654445303", "sector": "Communication Services",
     "shares": 6_000_000, "value_usd": 840_000_000, "pct_portfolio": 7.2},
    {"fund": "ValueAct Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Recruit Holdings (ADR)", "ticker": "RCRUY", "cusip": "75625L102", "sector": "Industrials",
     "shares": 8_000_000, "value_usd": 720_000_000, "pct_portfolio": 6.2},
    {"fund": "ValueAct Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Bausch Health Cos", "ticker": "BHC", "cusip": "071734104", "sector": "Healthcare",
     "shares": 25_000_000, "value_usd": 200_000_000, "pct_portfolio": 1.7},

    # ── Lone Pine Capital ──
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Meta Platforms Inc", "ticker": "META", "cusip": "30303M102", "sector": "Technology",
     "shares": 3_200_000, "value_usd": 1_875_000_000, "pct_portfolio": 12.5},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Microsoft Corp", "ticker": "MSFT", "cusip": "594918104", "sector": "Technology",
     "shares": 4_100_000, "value_usd": 1_722_000_000, "pct_portfolio": 11.5},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Uber Technologies Inc", "ticker": "UBER", "cusip": "90353T100", "sector": "Technology",
     "shares": 18_000_000, "value_usd": 1_110_000_000, "pct_portfolio": 7.4},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "ServiceNow Inc", "ticker": "NOW", "cusip": "81762P102", "sector": "Technology",
     "shares": 1_050_000, "value_usd": 1_102_000_000, "pct_portfolio": 7.3},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Amazon.com Inc", "ticker": "AMZN", "cusip": "023135106", "sector": "Technology",
     "shares": 4_500_000, "value_usd": 999_000_000, "pct_portfolio": 6.7},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Visa Inc", "ticker": "V", "cusip": "92826C839", "sector": "Financials",
     "shares": 3_000_000, "value_usd": 834_000_000, "pct_portfolio": 5.6},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Mastercard Inc", "ticker": "MA", "cusip": "57636Q104", "sector": "Financials",
     "shares": 1_400_000, "value_usd": 728_000_000, "pct_portfolio": 4.9},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Netflix Inc", "ticker": "NFLX", "cusip": "64110L106", "sector": "Communication Services",
     "shares": 700_000, "value_usd": 619_000_000, "pct_portfolio": 4.1},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Alphabet Inc (GOOG)", "ticker": "GOOG", "cusip": "02079K107", "sector": "Technology",
     "shares": 3_000_000, "value_usd": 578_000_000, "pct_portfolio": 3.9},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "Workday Inc", "ticker": "WDAY", "cusip": "98138H101", "sector": "Technology",
     "shares": 1_800_000, "value_usd": 468_000_000, "pct_portfolio": 3.1},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "ASML Holding NV", "ticker": "ASML", "cusip": "N07059202", "sector": "Technology",
     "shares": 600_000, "value_usd": 420_000_000, "pct_portfolio": 2.8},
    {"fund": "Lone Pine Capital", "quarter": "Q4 2024", "report_date": "2024-12-31",
     "company": "CrowdStrike Holdings", "ticker": "CRWD", "cusip": "22788C105", "sector": "Technology",
     "shares": 1_100_000, "value_usd": 385_000_000, "pct_portfolio": 2.6},
]

# ──────────────────────────────────────────────────────────────
# Q3 2024 Holdings (filed Nov 2024, reporting date: 2024-09-30)
# ──────────────────────────────────────────────────────────────

Q3_2024 = [
    # ── TCI Fund Management ──
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Visa Inc", "ticker": "V", "cusip": "92826C839", "sector": "Financials",
     "shares": 17_200_000, "value_usd": 4_730_000_000, "pct_portfolio": 17.8},
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Alphabet Inc (GOOG)", "ticker": "GOOG", "cusip": "02079K107", "sector": "Technology",
     "shares": 24_000_000, "value_usd": 3_984_000_000, "pct_portfolio": 15.0},
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Microsoft Corp", "ticker": "MSFT", "cusip": "594918104", "sector": "Technology",
     "shares": 8_500_000, "value_usd": 3_655_000_000, "pct_portfolio": 13.7},
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Canadian Pacific Kansas City", "ticker": "CP", "cusip": "13646K108", "sector": "Industrials",
     "shares": 42_000_000, "value_usd": 3_276_000_000, "pct_portfolio": 12.3},
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Moody's Corp", "ticker": "MCO", "cusip": "615369105", "sector": "Financials",
     "shares": 5_100_000, "value_usd": 2_295_000_000, "pct_portfolio": 8.6},
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "S&P Global Inc", "ticker": "SPGI", "cusip": "78409V104", "sector": "Financials",
     "shares": 4_200_000, "value_usd": 2_058_000_000, "pct_portfolio": 7.7},
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Charles Schwab Corp", "ticker": "SCHW", "cusip": "808513105", "sector": "Financials",
     "shares": 20_000_000, "value_usd": 1_340_000_000, "pct_portfolio": 5.0},
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Marsh & McLennan Cos", "ticker": "MMC", "cusip": "571748102", "sector": "Financials",
     "shares": 5_800_000, "value_usd": 1_160_000_000, "pct_portfolio": 4.4},
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "IQVIA Holdings Inc", "ticker": "IQV", "cusip": "46266C105", "sector": "Healthcare",
     "shares": 5_200_000, "value_usd": 1_196_000_000, "pct_portfolio": 4.5},
    {"fund": "TCI Fund Management", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Aon PLC", "ticker": "AON", "cusip": "G0408V102", "sector": "Financials",
     "shares": 2_100_000, "value_usd": 735_000_000, "pct_portfolio": 2.8},

    # ── Egerton Capital ──
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Microsoft Corp", "ticker": "MSFT", "cusip": "594918104", "sector": "Technology",
     "shares": 5_200_000, "value_usd": 2_236_000_000, "pct_portfolio": 15.2},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Amazon.com Inc", "ticker": "AMZN", "cusip": "023135106", "sector": "Technology",
     "shares": 6_500_000, "value_usd": 1_209_000_000, "pct_portfolio": 8.2},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Visa Inc", "ticker": "V", "cusip": "92826C839", "sector": "Financials",
     "shares": 4_500_000, "value_usd": 1_237_000_000, "pct_portfolio": 8.4},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Mastercard Inc", "ticker": "MA", "cusip": "57636Q104", "sector": "Financials",
     "shares": 2_400_000, "value_usd": 1_176_000_000, "pct_portfolio": 8.0},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Alphabet Inc (GOOG)", "ticker": "GOOG", "cusip": "02079K107", "sector": "Technology",
     "shares": 5_200_000, "value_usd": 863_000_000, "pct_portfolio": 5.9},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Meta Platforms Inc", "ticker": "META", "cusip": "30303M102", "sector": "Technology",
     "shares": 1_800_000, "value_usd": 1_026_000_000, "pct_portfolio": 7.0},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "ASML Holding NV", "ticker": "ASML", "cusip": "N07059202", "sector": "Technology",
     "shares": 900_000, "value_usd": 684_000_000, "pct_portfolio": 4.7},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "S&P Global Inc", "ticker": "SPGI", "cusip": "78409V104", "sector": "Financials",
     "shares": 1_400_000, "value_usd": 686_000_000, "pct_portfolio": 4.7},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Booking Holdings Inc", "ticker": "BKNG", "cusip": "09857L108", "sector": "Consumer Discretionary",
     "shares": 140_000, "value_usd": 584_000_000, "pct_portfolio": 4.0},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Moody's Corp", "ticker": "MCO", "cusip": "615369105", "sector": "Financials",
     "shares": 1_200_000, "value_usd": 540_000_000, "pct_portfolio": 3.7},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Uber Technologies Inc", "ticker": "UBER", "cusip": "90353T100", "sector": "Technology",
     "shares": 6_000_000, "value_usd": 456_000_000, "pct_portfolio": 3.1},
    {"fund": "Egerton Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Spotify Technology SA", "ticker": "SPOT", "cusip": "L8681T102", "sector": "Communication Services",
     "shares": 800_000, "value_usd": 288_000_000, "pct_portfolio": 2.0},

    # ── AKO Capital ──
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Microsoft Corp", "ticker": "MSFT", "cusip": "594918104", "sector": "Technology",
     "shares": 3_200_000, "value_usd": 1_376_000_000, "pct_portfolio": 16.1},
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "S&P Global Inc", "ticker": "SPGI", "cusip": "78409V104", "sector": "Financials",
     "shares": 2_000_000, "value_usd": 980_000_000, "pct_portfolio": 11.5},
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Visa Inc", "ticker": "V", "cusip": "92826C839", "sector": "Financials",
     "shares": 3_200_000, "value_usd": 880_000_000, "pct_portfolio": 10.3},
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Moody's Corp", "ticker": "MCO", "cusip": "615369105", "sector": "Financials",
     "shares": 1_600_000, "value_usd": 720_000_000, "pct_portfolio": 8.4},
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Mastercard Inc", "ticker": "MA", "cusip": "57636Q104", "sector": "Financials",
     "shares": 1_300_000, "value_usd": 637_000_000, "pct_portfolio": 7.5},
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "MSCI Inc", "ticker": "MSCI", "cusip": "55354G100", "sector": "Financials",
     "shares": 900_000, "value_usd": 504_000_000, "pct_portfolio": 5.9},
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Alphabet Inc (GOOG)", "ticker": "GOOG", "cusip": "02079K107", "sector": "Technology",
     "shares": 3_000_000, "value_usd": 498_000_000, "pct_portfolio": 5.8},
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Booking Holdings Inc", "ticker": "BKNG", "cusip": "09857L108", "sector": "Consumer Discretionary",
     "shares": 85_000, "value_usd": 355_000_000, "pct_portfolio": 4.2},
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Marsh & McLennan Cos", "ticker": "MMC", "cusip": "571748102", "sector": "Financials",
     "shares": 1_800_000, "value_usd": 360_000_000, "pct_portfolio": 4.2},
    {"fund": "AKO Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Accenture PLC", "ticker": "ACN", "cusip": "G1151C101", "sector": "Technology",
     "shares": 600_000, "value_usd": 210_000_000, "pct_portfolio": 2.5},

    # ── ValueAct Capital ──
    {"fund": "ValueAct Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Salesforce Inc", "ticker": "CRM", "cusip": "79466L302", "sector": "Technology",
     "shares": 8_500_000, "value_usd": 2_312_000_000, "pct_portfolio": 21.5},
    {"fund": "ValueAct Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Fiserv Inc", "ticker": "FI", "cusip": "337738108", "sector": "Financials",
     "shares": 9_200_000, "value_usd": 1_656_000_000, "pct_portfolio": 15.4},
    {"fund": "ValueAct Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "KKR & Co Inc", "ticker": "KKR", "cusip": "48251W104", "sector": "Financials",
     "shares": 7_500_000, "value_usd": 975_000_000, "pct_portfolio": 9.1},
    {"fund": "ValueAct Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Spotify Technology SA", "ticker": "SPOT", "cusip": "L8681T102", "sector": "Communication Services",
     "shares": 2_500_000, "value_usd": 900_000_000, "pct_portfolio": 8.4},
    {"fund": "ValueAct Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Insight Enterprises Inc", "ticker": "NSIT", "cusip": "45765U103", "sector": "Technology",
     "shares": 3_800_000, "value_usd": 722_000_000, "pct_portfolio": 6.7},
    {"fund": "ValueAct Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Heidrick & Struggles", "ticker": "HSII", "cusip": "422819102", "sector": "Industrials",
     "shares": 5_500_000, "value_usd": 187_000_000, "pct_portfolio": 1.7},
    {"fund": "ValueAct Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Nintendo Co Ltd (ADR)", "ticker": "NTDOY", "cusip": "654445303", "sector": "Communication Services",
     "shares": 5_000_000, "value_usd": 650_000_000, "pct_portfolio": 6.0},
    {"fund": "ValueAct Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Recruit Holdings (ADR)", "ticker": "RCRUY", "cusip": "75625L102", "sector": "Industrials",
     "shares": 7_000_000, "value_usd": 595_000_000, "pct_portfolio": 5.5},
    {"fund": "ValueAct Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Bausch Health Cos", "ticker": "BHC", "cusip": "071734104", "sector": "Healthcare",
     "shares": 25_000_000, "value_usd": 225_000_000, "pct_portfolio": 2.1},

    # ── Lone Pine Capital ──
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Meta Platforms Inc", "ticker": "META", "cusip": "30303M102", "sector": "Technology",
     "shares": 2_800_000, "value_usd": 1_596_000_000, "pct_portfolio": 11.2},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Microsoft Corp", "ticker": "MSFT", "cusip": "594918104", "sector": "Technology",
     "shares": 4_100_000, "value_usd": 1_763_000_000, "pct_portfolio": 12.4},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Uber Technologies Inc", "ticker": "UBER", "cusip": "90353T100", "sector": "Technology",
     "shares": 15_000_000, "value_usd": 1_140_000_000, "pct_portfolio": 8.0},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "ServiceNow Inc", "ticker": "NOW", "cusip": "81762P102", "sector": "Technology",
     "shares": 1_050_000, "value_usd": 945_000_000, "pct_portfolio": 6.6},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Amazon.com Inc", "ticker": "AMZN", "cusip": "023135106", "sector": "Technology",
     "shares": 5_500_000, "value_usd": 1_023_000_000, "pct_portfolio": 7.2},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Visa Inc", "ticker": "V", "cusip": "92826C839", "sector": "Financials",
     "shares": 3_000_000, "value_usd": 825_000_000, "pct_portfolio": 5.8},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Mastercard Inc", "ticker": "MA", "cusip": "57636Q104", "sector": "Financials",
     "shares": 1_400_000, "value_usd": 686_000_000, "pct_portfolio": 4.8},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Netflix Inc", "ticker": "NFLX", "cusip": "64110L106", "sector": "Communication Services",
     "shares": 500_000, "value_usd": 355_000_000, "pct_portfolio": 2.5},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Alphabet Inc (GOOG)", "ticker": "GOOG", "cusip": "02079K107", "sector": "Technology",
     "shares": 3_500_000, "value_usd": 581_000_000, "pct_portfolio": 4.1},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "Workday Inc", "ticker": "WDAY", "cusip": "98138H101", "sector": "Technology",
     "shares": 2_200_000, "value_usd": 528_000_000, "pct_portfolio": 3.7},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "CrowdStrike Holdings", "ticker": "CRWD", "cusip": "22788C105", "sector": "Technology",
     "shares": 1_500_000, "value_usd": 420_000_000, "pct_portfolio": 3.0},
    {"fund": "Lone Pine Capital", "quarter": "Q3 2024", "report_date": "2024-09-30",
     "company": "ASML Holding NV", "ticker": "ASML", "cusip": "N07059202", "sector": "Technology",
     "shares": 600_000, "value_usd": 456_000_000, "pct_portfolio": 3.2},
]


def get_all_holdings() -> pd.DataFrame:
    """Return all holdings across all quarters as a single DataFrame."""
    all_data = Q4_2024 + Q3_2024
    df = pd.DataFrame(all_data)
    df["report_date"] = pd.to_datetime(df["report_date"])
    df["value_bn"] = df["value_usd"] / 1e9
    df["value_mn"] = df["value_usd"] / 1e6
    # Map fund names to short names
    df["fund_short"] = df["fund"].map(lambda f: FUNDS[f]["short_name"])
    return df


def get_quarter_holdings(quarter: str) -> pd.DataFrame:
    """Get holdings for a specific quarter (e.g., 'Q4 2024')."""
    df = get_all_holdings()
    return df[df["quarter"] == quarter].copy()


def get_fund_holdings(fund_name: str) -> pd.DataFrame:
    """Get all holdings for a specific fund across all quarters."""
    df = get_all_holdings()
    return df[df["fund"] == fund_name].copy()


def compute_changes(fund_name: str, current_q: str = "Q4 2024", prior_q: str = "Q3 2024") -> pd.DataFrame:
    """Compute quarter-over-quarter changes for a fund."""
    df = get_all_holdings()
    curr = df[(df["fund"] == fund_name) & (df["quarter"] == current_q)].set_index("ticker")
    prev = df[(df["fund"] == fund_name) & (df["quarter"] == prior_q)].set_index("ticker")

    all_tickers = set(curr.index) | set(prev.index)
    changes = []

    for ticker in all_tickers:
        in_curr = ticker in curr.index
        in_prev = ticker in prev.index

        row = {
            "ticker": ticker,
            "company": curr.loc[ticker, "company"] if in_curr else prev.loc[ticker, "company"],
            "sector": curr.loc[ticker, "sector"] if in_curr else prev.loc[ticker, "sector"],
        }

        if in_curr and in_prev:
            row["curr_shares"] = curr.loc[ticker, "shares"]
            row["prev_shares"] = prev.loc[ticker, "shares"]
            row["curr_value"] = curr.loc[ticker, "value_usd"]
            row["prev_value"] = prev.loc[ticker, "value_usd"]
            row["share_change"] = curr.loc[ticker, "shares"] - prev.loc[ticker, "shares"]
            row["share_change_pct"] = (row["share_change"] / prev.loc[ticker, "shares"]) * 100
            row["value_change"] = curr.loc[ticker, "value_usd"] - prev.loc[ticker, "value_usd"]
            if row["share_change"] > 0:
                row["action"] = "Increased"
            elif row["share_change"] < 0:
                row["action"] = "Reduced"
            else:
                row["action"] = "Unchanged"
        elif in_curr and not in_prev:
            row["curr_shares"] = curr.loc[ticker, "shares"]
            row["prev_shares"] = 0
            row["curr_value"] = curr.loc[ticker, "value_usd"]
            row["prev_value"] = 0
            row["share_change"] = curr.loc[ticker, "shares"]
            row["share_change_pct"] = 100.0
            row["value_change"] = curr.loc[ticker, "value_usd"]
            row["action"] = "New Position"
        else:
            row["curr_shares"] = 0
            row["prev_shares"] = prev.loc[ticker, "shares"]
            row["curr_value"] = 0
            row["prev_value"] = prev.loc[ticker, "value_usd"]
            row["share_change"] = -prev.loc[ticker, "shares"]
            row["share_change_pct"] = -100.0
            row["value_change"] = -prev.loc[ticker, "value_usd"]
            row["action"] = "Sold Out"

        changes.append(row)

    return pd.DataFrame(changes).sort_values("curr_value", ascending=False)


def get_cross_fund_holdings(quarter: str = "Q4 2024") -> pd.DataFrame:
    """Find stocks held by multiple funds in a given quarter."""
    df = get_quarter_holdings(quarter)
    grouped = df.groupby("ticker").agg(
        company=("company", "first"),
        sector=("sector", "first"),
        num_funds=("fund_short", "nunique"),
        funds=("fund_short", lambda x: ", ".join(sorted(x.unique()))),
        total_value=("value_usd", "sum"),
        total_shares=("shares", "sum"),
    ).reset_index()
    return grouped.sort_values("num_funds", ascending=False)
