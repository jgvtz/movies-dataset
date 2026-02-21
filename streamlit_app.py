import altair as alt
import pandas as pd
import streamlit as st

from data.fund_holdings import (
    FUNDS,
    get_all_holdings,
)
from data.sec_edgar import (
    FUND_CIKS,
    fetch_fund_holdings as sec_fetch_fund_holdings,
)

# ─── Page Config ─────────────────────────────────────────────
st.set_page_config(
    page_title="13F Fund Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="stMetric"] label { font-size: 0.8rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        border-radius: 6px 6px 0 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── CUSIP Lookup (from known 13F data) ─────────────────────
# 13F filings don't include tickers/sectors, so we map CUSIPs
CUSIP_LOOKUP = {
    "92826C839": {"ticker": "V", "sector": "Financials"},
    "02079K107": {"ticker": "GOOG", "sector": "Technology"},
    "594918104": {"ticker": "MSFT", "sector": "Technology"},
    "13646K108": {"ticker": "CP", "sector": "Industrials"},
    "615369105": {"ticker": "MCO", "sector": "Financials"},
    "78409V104": {"ticker": "SPGI", "sector": "Financials"},
    "808513105": {"ticker": "SCHW", "sector": "Financials"},
    "571748102": {"ticker": "MMC", "sector": "Financials"},
    "46266C105": {"ticker": "IQV", "sector": "Healthcare"},
    "G0408V102": {"ticker": "AON", "sector": "Financials"},
    "023135106": {"ticker": "AMZN", "sector": "Technology"},
    "57636Q104": {"ticker": "MA", "sector": "Financials"},
    "30303M102": {"ticker": "META", "sector": "Technology"},
    "N07059202": {"ticker": "ASML", "sector": "Technology"},
    "09857L108": {"ticker": "BKNG", "sector": "Consumer Discretionary"},
    "90353T100": {"ticker": "UBER", "sector": "Technology"},
    "64110L106": {"ticker": "NFLX", "sector": "Communication Services"},
    "L8681T102": {"ticker": "SPOT", "sector": "Communication Services"},
    "55354G100": {"ticker": "MSCI", "sector": "Financials"},
    "G1151C101": {"ticker": "ACN", "sector": "Technology"},
    "79466L302": {"ticker": "CRM", "sector": "Technology"},
    "337738108": {"ticker": "FI", "sector": "Financials"},
    "48251W104": {"ticker": "KKR", "sector": "Financials"},
    "45765U103": {"ticker": "NSIT", "sector": "Technology"},
    "422819102": {"ticker": "HSII", "sector": "Industrials"},
    "654445303": {"ticker": "NTDOY", "sector": "Communication Services"},
    "75625L102": {"ticker": "RCRUY", "sector": "Industrials"},
    "071734104": {"ticker": "BHC", "sector": "Healthcare"},
    "81762P102": {"ticker": "NOW", "sector": "Technology"},
    "98138H101": {"ticker": "WDAY", "sector": "Technology"},
    "22788C105": {"ticker": "CRWD", "sector": "Technology"},
}

# Reverse: short name -> full name for the FUND_CIKS keys
FUND_SHORT_NAMES = {name: info["short_name"] for name, info in FUNDS.items()}


def _enrich_live_data(df: pd.DataFrame) -> pd.DataFrame:
    """Add ticker, sector, and fund_short columns to live SEC data."""
    df = df.copy()
    df["ticker"] = df["cusip"].map(lambda c: CUSIP_LOOKUP.get(c, {}).get("ticker", c[:6]))
    df["sector"] = df["cusip"].map(lambda c: CUSIP_LOOKUP.get(c, {}).get("sector", "Other"))
    df["fund_short"] = df["fund"].map(lambda f: FUNDS.get(f, {}).get("short_name", f))
    return df


# ─── Data Loading ────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_live_data() -> tuple[pd.DataFrame, bool, str]:
    """Try to fetch live data from SEC EDGAR, fall back to sample data."""
    try:
        all_dfs = []
        for fund_name, cik in FUND_CIKS.items():
            df = sec_fetch_fund_holdings(fund_name, cik, num_quarters=2)
            if not df.empty:
                all_dfs.append(df)
        if all_dfs:
            combined = pd.concat(all_dfs, ignore_index=True)
            combined = _enrich_live_data(combined)
            return combined, True, ""
        return get_all_holdings(), False, "SEC returned empty data for all funds"
    except Exception as e:
        return get_all_holdings(), False, str(e)


df_all, is_live, _load_error = load_live_data()
quarters = sorted(df_all["quarter"].unique(), reverse=True)
latest_q = quarters[0]
prior_q = quarters[1] if len(quarters) > 1 else None


def _get_quarter(quarter: str) -> pd.DataFrame:
    return df_all[df_all["quarter"] == quarter].copy()


def _cross_fund(quarter: str) -> pd.DataFrame:
    df = _get_quarter(quarter)
    grouped = df.groupby("ticker").agg(
        company=("company", "first"),
        sector=("sector", "first"),
        num_funds=("fund_short", "nunique"),
        funds=("fund_short", lambda x: ", ".join(sorted(x.unique()))),
        total_value=("value_usd", "sum"),
        total_shares=("shares", "sum"),
    ).reset_index()
    return grouped.sort_values("num_funds", ascending=False)


def _compute_changes(fund_name: str, current_q: str, prior_q_name: str) -> pd.DataFrame:
    curr = df_all[(df_all["fund"] == fund_name) & (df_all["quarter"] == current_q)].copy()
    prev = df_all[(df_all["fund"] == fund_name) & (df_all["quarter"] == prior_q_name)].copy()
    curr = curr.set_index("ticker")
    prev = prev.set_index("ticker")
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
            row["share_change_pct"] = (row["share_change"] / prev.loc[ticker, "shares"]) * 100 if prev.loc[ticker, "shares"] else 0
            row["value_change"] = curr.loc[ticker, "value_usd"] - prev.loc[ticker, "value_usd"]
            if row["share_change"] > 0:
                row["action"] = "Increased"
            elif row["share_change"] < 0:
                row["action"] = "Reduced"
            else:
                row["action"] = "Unchanged"
        elif in_curr:
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

# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.title("13F Fund Tracker")
    if is_live:
        st.success("Live data from SEC EDGAR")
        filing_dates = df_all["filing_date"].dropna().unique()
        if len(filing_dates) > 0:
            latest_filing = max(filing_dates)
            st.caption(f"Latest filing: {latest_filing}")
    else:
        st.warning("Using sample data (SEC EDGAR unavailable)")
        if _load_error:
            st.caption(f"Error: {_load_error}")
    st.divider()

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Fund Deep Dive",
            "Position Changes",
            "Cross-Fund Analysis",
            "Conviction Heatmap",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**Tracked Funds**")
    for name, info in FUNDS.items():
        st.markdown(f"- **{info['short_name']}** — {info['style']}")

    st.divider()
    st.caption(
        "Data based on 13F-HR filings. All information is public, "
        "disclosed quarterly by institutional investment managers per SEC regulations. "
        "Not investment advice."
    )


# ═══════════════════════════════════════════════════════════════
#  PAGE: Overview
# ═══════════════════════════════════════════════════════════════
if page == "Overview":
    st.header("Portfolio Overview")
    st.caption(f"Reporting period: {latest_q}")

    # ── Fund Summary Metrics ──
    df_latest = df_all[df_all["quarter"] == latest_q].copy()
    fund_summary = (
        df_latest.groupby("fund_short")
        .agg(
            total_value=("value_usd", "sum"),
            num_positions=("ticker", "nunique"),
            top_holding_pct=("pct_portfolio", "max"),
        )
        .reset_index()
        .sort_values("total_value", ascending=False)
    )

    cols = st.columns(len(fund_summary))
    for i, (_, row) in enumerate(fund_summary.iterrows()):
        with cols[i]:
            st.metric(
                label=row["fund_short"],
                value=f"${row['total_value'] / 1e9:.1f}B",
                delta=f"{row['num_positions']} positions",
            )
            st.caption(f"Top position: {row['top_holding_pct']:.1f}% of portfolio")

    st.divider()

    # ── Top Holdings by Fund ──
    st.subheader("Top 5 Holdings per Fund")

    fund_tabs = st.tabs([FUNDS[f]["short_name"] for f in FUNDS])
    for tab, fund_name in zip(fund_tabs, FUNDS):
        with tab:
            df_fund = df_latest[df_latest["fund"] == fund_name].nlargest(5, "value_usd")
            chart = (
                alt.Chart(df_fund)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                .encode(
                    x=alt.X("value_bn:Q", title="Value ($B)"),
                    y=alt.Y("ticker:N", sort="-x", title=""),
                    color=alt.Color(
                        "pct_portfolio:Q",
                        scale=alt.Scale(scheme="blues"),
                        title="% of Portfolio",
                    ),
                    tooltip=[
                        alt.Tooltip("company:N", title="Company"),
                        alt.Tooltip("ticker:N", title="Ticker"),
                        alt.Tooltip("value_bn:Q", title="Value ($B)", format=".2f"),
                        alt.Tooltip("pct_portfolio:Q", title="% Portfolio", format=".1f"),
                        alt.Tooltip("shares:Q", title="Shares", format=","),
                    ],
                )
                .properties(height=220)
            )
            st.altair_chart(chart, use_container_width=True)

    st.divider()

    # ── Sector Allocation ──
    st.subheader("Sector Allocation Across Funds")

    sector_data = (
        df_latest.groupby(["fund_short", "sector"])
        .agg(total_value=("value_usd", "sum"))
        .reset_index()
    )
    # Compute percentage within each fund
    fund_totals = sector_data.groupby("fund_short")["total_value"].transform("sum")
    sector_data["pct"] = (sector_data["total_value"] / fund_totals * 100).round(1)

    sector_chart = (
        alt.Chart(sector_data)
        .mark_bar()
        .encode(
            x=alt.X("pct:Q", title="% of Portfolio", stack="normalize"),
            y=alt.Y("fund_short:N", title="", sort="-x"),
            color=alt.Color(
                "sector:N",
                scale=alt.Scale(scheme="tableau10"),
                title="Sector",
            ),
            tooltip=[
                alt.Tooltip("fund_short:N", title="Fund"),
                alt.Tooltip("sector:N", title="Sector"),
                alt.Tooltip("pct:Q", title="% of Portfolio", format=".1f"),
            ],
        )
        .properties(height=250)
    )
    st.altair_chart(sector_chart, use_container_width=True)

    # ── Full Holdings Table ──
    st.subheader("All Holdings")
    fund_filter = st.multiselect(
        "Filter by fund",
        options=list(FUNDS.keys()),
        default=list(FUNDS.keys()),
        format_func=lambda x: FUNDS[x]["short_name"],
    )
    df_table = df_latest[df_latest["fund"].isin(fund_filter)][
        ["fund_short", "company", "ticker", "sector", "shares", "value_mn", "pct_portfolio"]
    ].sort_values("value_mn", ascending=False)
    df_table.columns = ["Fund", "Company", "Ticker", "Sector", "Shares", "Value ($M)", "% Portfolio"]

    st.dataframe(
        df_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Shares": st.column_config.NumberColumn(format="%d"),
            "Value ($M)": st.column_config.NumberColumn(format="$%.0f"),
            "% Portfolio": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

# ═══════════════════════════════════════════════════════════════
#  PAGE: Fund Deep Dive
# ═══════════════════════════════════════════════════════════════
elif page == "Fund Deep Dive":
    st.header("Fund Deep Dive")

    selected_fund = st.selectbox(
        "Select Fund",
        list(FUNDS.keys()),
        format_func=lambda x: f"{FUNDS[x]['short_name']} — {FUNDS[x]['description']}",
    )

    fund_info = FUNDS[selected_fund]
    df_fund_latest = df_all[(df_all["fund"] == selected_fund) & (df_all["quarter"] == latest_q)]
    total_value = df_fund_latest["value_usd"].sum()
    num_positions = df_fund_latest["ticker"].nunique()
    top_5_pct = df_fund_latest.nlargest(5, "value_usd")["pct_portfolio"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("13F AUM", f"${total_value / 1e9:.1f}B")
    col2.metric("Positions", num_positions)
    col3.metric("Top 5 Concentration", f"{top_5_pct:.1f}%")
    col4.metric("Style", fund_info["style"])

    st.divider()

    # ── Holdings Breakdown ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Holdings by Value")
        df_sorted = df_fund_latest.sort_values("value_usd", ascending=True)
        chart = (
            alt.Chart(df_sorted)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
            .encode(
                x=alt.X("value_bn:Q", title="Value ($B)"),
                y=alt.Y("ticker:N", sort="-x", title=""),
                color=alt.Color(
                    "sector:N",
                    scale=alt.Scale(scheme="tableau10"),
                    title="Sector",
                ),
                tooltip=[
                    alt.Tooltip("company:N", title="Company"),
                    alt.Tooltip("value_bn:Q", title="Value ($B)", format=".2f"),
                    alt.Tooltip("pct_portfolio:Q", title="% Portfolio", format=".1f"),
                    alt.Tooltip("shares:Q", title="Shares", format=","),
                    alt.Tooltip("sector:N", title="Sector"),
                ],
            )
            .properties(height=max(300, num_positions * 35))
        )
        st.altair_chart(chart, use_container_width=True)

    with col_right:
        st.subheader("Portfolio Concentration")
        # Donut chart showing top holdings
        df_donut = df_fund_latest.nlargest(7, "value_usd").copy()
        others_pct = 100 - df_donut["pct_portfolio"].sum()
        if others_pct > 0:
            df_donut = pd.concat([
                df_donut,
                pd.DataFrame([{
                    "ticker": "Others",
                    "company": "Remaining positions",
                    "pct_portfolio": others_pct,
                    "value_usd": total_value * others_pct / 100,
                }]),
            ], ignore_index=True)

        donut = (
            alt.Chart(df_donut)
            .mark_arc(innerRadius=60, outerRadius=120)
            .encode(
                theta=alt.Theta("pct_portfolio:Q"),
                color=alt.Color("ticker:N", title="Holding", scale=alt.Scale(scheme="tableau10")),
                tooltip=[
                    alt.Tooltip("ticker:N", title="Ticker"),
                    alt.Tooltip("company:N", title="Company"),
                    alt.Tooltip("pct_portfolio:Q", title="% Portfolio", format=".1f"),
                ],
            )
            .properties(height=300)
        )
        st.altair_chart(donut, use_container_width=True)

        st.subheader("Sector Weights")
        sector_weights = (
            df_fund_latest.groupby("sector")["pct_portfolio"]
            .sum()
            .reset_index()
            .sort_values("pct_portfolio", ascending=False)
        )
        sector_weights.columns = ["Sector", "Weight (%)"]
        st.dataframe(
            sector_weights,
            use_container_width=True,
            hide_index=True,
            column_config={"Weight (%)": st.column_config.NumberColumn(format="%.1f%%")},
        )

    # ── Detailed Table ──
    st.divider()
    st.subheader("Detailed Holdings")
    detail_df = df_fund_latest[
        ["ticker", "company", "sector", "shares", "value_mn", "pct_portfolio"]
    ].sort_values("value_mn", ascending=False)
    detail_df.columns = ["Ticker", "Company", "Sector", "Shares", "Value ($M)", "% Portfolio"]
    st.dataframe(
        detail_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Shares": st.column_config.NumberColumn(format="%d"),
            "Value ($M)": st.column_config.NumberColumn(format="$%.0f"),
            "% Portfolio": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )


# ═══════════════════════════════════════════════════════════════
#  PAGE: Position Changes
# ═══════════════════════════════════════════════════════════════
elif page == "Position Changes":
    st.header("Quarter-over-Quarter Changes")
    st.caption(f"{prior_q} → {latest_q}")

    selected_fund = st.selectbox(
        "Select Fund",
        list(FUNDS.keys()),
        format_func=lambda x: FUNDS[x]["short_name"],
    )

    if prior_q:
        changes = _compute_changes(selected_fund, latest_q, prior_q)

        # ── Summary Metrics ──
        new_positions = changes[changes["action"] == "New Position"]
        sold_positions = changes[changes["action"] == "Sold Out"]
        increased = changes[changes["action"] == "Increased"]
        reduced = changes[changes["action"] == "Reduced"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("New Positions", len(new_positions), delta="added", delta_color="normal")
        c2.metric("Sold Out", len(sold_positions), delta="removed", delta_color="inverse")
        c3.metric("Increased", len(increased), delta="added shares", delta_color="normal")
        c4.metric("Reduced", len(reduced), delta="trimmed", delta_color="inverse")

        st.divider()

        # ── Changes Visualization ──
        changes_viz = changes[changes["action"] != "Unchanged"].copy()
        if not changes_viz.empty:
            changes_viz["share_change_pct_display"] = changes_viz["share_change_pct"].clip(-100, 200)

            # Color based on action
            color_map = {
                "New Position": "#2ecc71",
                "Increased": "#27ae60",
                "Reduced": "#e74c3c",
                "Sold Out": "#c0392b",
            }

            st.subheader("Share Changes by Position")

            change_chart = (
                alt.Chart(changes_viz)
                .mark_bar(cornerRadius=3)
                .encode(
                    x=alt.X("share_change_pct_display:Q", title="Share Change (%)"),
                    y=alt.Y("ticker:N", sort=alt.EncodingSortField(field="share_change_pct", order="descending"), title=""),
                    color=alt.Color(
                        "action:N",
                        scale=alt.Scale(
                            domain=list(color_map.keys()),
                            range=list(color_map.values()),
                        ),
                        title="Action",
                    ),
                    tooltip=[
                        alt.Tooltip("company:N", title="Company"),
                        alt.Tooltip("ticker:N", title="Ticker"),
                        alt.Tooltip("action:N", title="Action"),
                        alt.Tooltip("share_change:Q", title="Share Change", format=","),
                        alt.Tooltip("share_change_pct:Q", title="Change %", format=".1f"),
                        alt.Tooltip("curr_value:Q", title="Current Value ($)", format=",.0f"),
                    ],
                )
                .properties(height=max(250, len(changes_viz) * 30))
            )
            st.altair_chart(change_chart, use_container_width=True)

        # ── Detailed Changes Table ──
        st.divider()
        st.subheader("Detailed Changes")

        action_filter = st.multiselect(
            "Filter by action",
            ["New Position", "Increased", "Reduced", "Sold Out", "Unchanged"],
            default=["New Position", "Increased", "Reduced", "Sold Out"],
        )

        filtered = changes[changes["action"].isin(action_filter)].copy()
        display_df = filtered[
            ["ticker", "company", "sector", "action", "prev_shares", "curr_shares",
             "share_change", "share_change_pct", "curr_value"]
        ].copy()
        display_df["curr_value"] = display_df["curr_value"] / 1e6
        display_df.columns = [
            "Ticker", "Company", "Sector", "Action", "Prev Shares", "Curr Shares",
            "Share Change", "Change %", "Curr Value ($M)",
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Prev Shares": st.column_config.NumberColumn(format="%d"),
                "Curr Shares": st.column_config.NumberColumn(format="%d"),
                "Share Change": st.column_config.NumberColumn(format="%d"),
                "Change %": st.column_config.NumberColumn(format="%.1f%%"),
                "Curr Value ($M)": st.column_config.NumberColumn(format="$%.0f"),
            },
        )
    else:
        st.info("Need at least 2 quarters of data to show changes.")


# ═══════════════════════════════════════════════════════════════
#  PAGE: Cross-Fund Analysis
# ═══════════════════════════════════════════════════════════════
elif page == "Cross-Fund Analysis":
    st.header("Cross-Fund Analysis")
    st.caption(f"Stocks held by multiple funds — {latest_q}")

    cross = _cross_fund(latest_q)

    # ── High-Conviction Ideas (held by 3+ funds) ──
    st.subheader("High-Conviction Ideas")
    st.markdown("Stocks held by **3 or more** tracked funds — potential starting points for deeper research.")

    high_conviction = cross[cross["num_funds"] >= 3].sort_values("num_funds", ascending=False)

    if not high_conviction.empty:
        for _, row in high_conviction.iterrows():
            with st.container():
                cols = st.columns([1, 2, 1, 2])
                cols[0].metric(row["ticker"], f"{row['num_funds']} funds")
                cols[1].write(f"**{row['company']}** — {row['sector']}")
                cols[2].metric("Total Value", f"${row['total_value'] / 1e9:.1f}B")
                cols[3].write(f"Held by: **{row['funds']}**")
            st.divider()
    else:
        st.info("No stocks held by 3+ funds in this quarter.")

    # ── Overlap Matrix ──
    st.subheader("Fund Overlap")
    st.markdown("How many stocks each pair of funds has in common.")

    df_latest = _get_quarter(latest_q)
    fund_names = sorted(df_latest["fund_short"].unique())
    fund_tickers = {
        fund: set(df_latest[df_latest["fund_short"] == fund]["ticker"])
        for fund in fund_names
    }

    overlap_data = []
    for f1 in fund_names:
        for f2 in fund_names:
            common = len(fund_tickers[f1] & fund_tickers[f2])
            overlap_data.append({"Fund A": f1, "Fund B": f2, "Common Holdings": common})

    overlap_df = pd.DataFrame(overlap_data)
    overlap_chart = (
        alt.Chart(overlap_df)
        .mark_rect(cornerRadius=4)
        .encode(
            x=alt.X("Fund A:N", title=""),
            y=alt.Y("Fund B:N", title=""),
            color=alt.Color(
                "Common Holdings:Q",
                scale=alt.Scale(scheme="blues"),
                title="# Common",
            ),
            tooltip=[
                alt.Tooltip("Fund A:N"),
                alt.Tooltip("Fund B:N"),
                alt.Tooltip("Common Holdings:Q"),
            ],
        )
        .properties(height=300, width=300)
    )
    text = (
        alt.Chart(overlap_df)
        .mark_text(fontSize=14, fontWeight="bold")
        .encode(
            x="Fund A:N",
            y="Fund B:N",
            text="Common Holdings:Q",
            color=alt.condition(
                alt.datum["Common Holdings"] > 4,
                alt.value("white"),
                alt.value("black"),
            ),
        )
    )
    st.altair_chart(overlap_chart + text, use_container_width=True)

    # ── All Cross-Holdings Table ──
    st.subheader("All Shared Positions")
    shared = cross[cross["num_funds"] >= 2].sort_values(["num_funds", "total_value"], ascending=[False, False])
    display_shared = shared[["ticker", "company", "sector", "num_funds", "funds", "total_value"]].copy()
    display_shared["total_value"] = display_shared["total_value"] / 1e9
    display_shared.columns = ["Ticker", "Company", "Sector", "# Funds", "Funds", "Total Value ($B)"]

    st.dataframe(
        display_shared,
        use_container_width=True,
        hide_index=True,
        column_config={
            "# Funds": st.column_config.NumberColumn(format="%d"),
            "Total Value ($B)": st.column_config.NumberColumn(format="$%.2f"),
        },
    )


# ═══════════════════════════════════════════════════════════════
#  PAGE: Conviction Heatmap
# ═══════════════════════════════════════════════════════════════
elif page == "Conviction Heatmap":
    st.header("Conviction Heatmap")
    st.caption(f"Portfolio weight (%) each fund allocates to shared positions — {latest_q}")

    df_latest = _get_quarter(latest_q)

    # Get stocks held by 2+ funds
    cross = _cross_fund(latest_q)
    shared_tickers = cross[cross["num_funds"] >= 2]["ticker"].tolist()

    if shared_tickers:
        # Build heatmap data
        heatmap_rows = []
        for _, row in df_latest[df_latest["ticker"].isin(shared_tickers)].iterrows():
            heatmap_rows.append({
                "ticker": row["ticker"],
                "company": row["company"],
                "fund": row["fund_short"],
                "pct_portfolio": row["pct_portfolio"],
            })

        heatmap_df = pd.DataFrame(heatmap_rows)

        # Order tickers by total conviction
        ticker_order = (
            heatmap_df.groupby("ticker")["pct_portfolio"]
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
        )

        heatmap = (
            alt.Chart(heatmap_df)
            .mark_rect(cornerRadius=3)
            .encode(
                x=alt.X("fund:N", title="", sort=sorted(FUNDS.keys(), key=lambda x: FUNDS[x]["short_name"])),
                y=alt.Y("ticker:N", title="", sort=ticker_order),
                color=alt.Color(
                    "pct_portfolio:Q",
                    scale=alt.Scale(scheme="orangered", domain=[0, 20]),
                    title="% Portfolio",
                ),
                tooltip=[
                    alt.Tooltip("ticker:N", title="Ticker"),
                    alt.Tooltip("company:N", title="Company"),
                    alt.Tooltip("fund:N", title="Fund"),
                    alt.Tooltip("pct_portfolio:Q", title="% Portfolio", format=".1f"),
                ],
            )
            .properties(height=max(400, len(ticker_order) * 30))
        )
        text_heatmap = (
            alt.Chart(heatmap_df)
            .mark_text(fontSize=11)
            .encode(
                x=alt.X("fund:N", sort=sorted(FUNDS.keys(), key=lambda x: FUNDS[x]["short_name"])),
                y=alt.Y("ticker:N", sort=ticker_order),
                text=alt.Text("pct_portfolio:Q", format=".1f"),
                color=alt.condition(
                    alt.datum.pct_portfolio > 10,
                    alt.value("white"),
                    alt.value("black"),
                ),
            )
        )
        st.altair_chart(heatmap + text_heatmap, use_container_width=True)

        st.divider()
        st.markdown("""
        **How to read this:**
        - Darker cells = higher conviction (larger % of that fund's portfolio)
        - Look for stocks where **multiple funds** have **high conviction** (dark cells across the row)
        - These represent potential research candidates where multiple respected investors have independently arrived at similar conclusions
        """)
    else:
        st.info("No shared positions found across funds.")
