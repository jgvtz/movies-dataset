# 13F Fund Tracker

A Streamlit dashboard that tracks 13F filings from SEC EDGAR for institutional investors you follow. Inspired by [13f.info](https://13f.info/).

## Tracked Funds

| Fund | Style | CIK |
|------|-------|-----|
| **TCI** (The Children's Investment Fund) | Concentrated Quality | 0001647251 |
| **Egerton Capital** | Quality Growth | 0001535392 |
| **AKO Capital** | Quality Growth | 0001606058 |
| **ValueAct Capital** | Activist / Concentrated | 0001418814 |
| **Lone Pine Capital** | Growth / Tiger Cub | 0001061768 |

## Features

- **Overview** — Portfolio summaries, top holdings per fund, sector allocation
- **Fund Deep Dive** — Detailed breakdown of any fund's holdings with concentration analysis
- **Position Changes** — Quarter-over-quarter changes (new positions, increases, reductions, exits)
- **Cross-Fund Analysis** — Stocks held by multiple funds, overlap matrix, high-conviction ideas
- **Conviction Heatmap** — Visual map of portfolio weights across shared positions

## How to run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   streamlit run streamlit_app.py
   ```

## Data

All data is public information disclosed quarterly by institutional investment managers with >$100M AUM per SEC regulations. The app includes:

- **Sample data** (`data/fund_holdings.py`) — Realistic holdings based on recent 13F filings
- **SEC EDGAR fetcher** (`data/sec_edgar.py`) — Module to pull live data from SEC EDGAR API

## Disclaimer

This tool is for informational and research purposes only. Not investment advice. Always conduct your own due diligence.
