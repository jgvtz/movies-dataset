import altair as alt
import pandas as pd
import streamlit as st

from data.fund_holdings import (
    FUNDS,
    compute_changes,
    get_all_holdings,
    get_cross_fund_holdings,
    get_quarter_holdings,
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


# ─── Data Loading ────────────────────────────────────────────
@st.cache_data
def load_data():
    return get_all_holdings()


df_all = load_data()
quarters = sorted(df_all["quarter"].unique(), reverse=True)
latest_q = quarters[0]
prior_q = quarters[1] if len(quarters) > 1 else None

# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.title("13F Fund Tracker")
    st.caption("Public 13F filings from SEC EDGAR")
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
    df_latest = get_quarter_holdings(latest_q)
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
        changes = compute_changes(selected_fund, latest_q, prior_q)

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

    cross = get_cross_fund_holdings(latest_q)

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

    df_latest = get_quarter_holdings(latest_q)
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

    df_latest = get_quarter_holdings(latest_q)

    # Get stocks held by 2+ funds
    cross = get_cross_fund_holdings(latest_q)
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
