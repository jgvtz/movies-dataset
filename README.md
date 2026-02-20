# 13F Fund Tracker

Track 13F filings from top institutional investors. Inspired by [13f.info](https://13f.info/).

Built as a research tool for the first layer of an investment process — finding potential opportunities from public SEC filings, before conducting deep fundamental research.

## Tracked Funds

| Fund | Style | CIK |
|------|-------|-----|
| **TCI** (The Children's Investment Fund) | Concentrated Quality | 0001647251 |
| **Egerton Capital** | Quality Growth | 0001535392 |
| **AKO Capital** | Quality Growth | 0001606058 |
| **ValueAct Capital** | Activist / Concentrated | 0001418814 |
| **Lone Pine Capital** | Growth / Tiger Cub | 0001061768 |

## Web App

A Flask application with Tailwind CSS + Chart.js frontend.

**Pages:**
- **Overview** — Fund AUM, top holdings per fund, sector allocation
- **Fund Deep Dive** — Full holdings breakdown, concentration donut, sector weights
- **Position Changes** — Quarter-over-quarter activity (new / increased / reduced / sold)
- **Cross-Fund Analysis** — Overlap matrix, conviction heatmap, high-conviction ideas (3+ funds)

### Run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000

## Telegram Bot

Get portfolio summaries and alerts on your phone.

### Setup

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the token and run:

```bash
export TELEGRAM_BOT_TOKEN="your-token-here"
python telegram_bot.py
```

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/overview` | All funds summary |
| `/fund TCI` | Deep dive into a specific fund |
| `/changes TCI` | Quarter-over-quarter changes |
| `/crossfund` | Stocks held by multiple funds |
| `/conviction` | High-conviction ideas (3+ funds) with conviction bars |

## Project Structure

```
app.py                  Flask web application
telegram_bot.py         Telegram bot
templates/index.html    Frontend (Tailwind + Chart.js)
data/
  fund_holdings.py      Holdings data + analysis functions
  sec_edgar.py          SEC EDGAR live data fetcher
```

## Data

All data is public information disclosed quarterly by institutional investment managers with >$100M AUM per SEC regulations.

- `data/fund_holdings.py` — Sample data based on Q3/Q4 2024 13F filings
- `data/sec_edgar.py` — Module to pull live data from SEC EDGAR API

## Disclaimer

This tool is for informational and research purposes only. Not investment advice. Always conduct your own due diligence.
