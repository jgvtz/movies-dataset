"""
13F Fund Tracker — Telegram Bot
================================
Sends portfolio summaries, changes, and cross-fund insights on demand.

Setup:
  1. Create a bot via @BotFather on Telegram → get your BOT_TOKEN
  2. Set environment variable:  export TELEGRAM_BOT_TOKEN="your-token-here"
  3. Run:  python telegram_bot.py

Commands:
  /start       — Welcome message
  /overview    — All funds summary
  /fund <name> — Deep dive (e.g. /fund TCI)
  /changes <name> — Quarter-over-quarter changes
  /crossfund   — Stocks held by multiple funds
  /conviction  — High-conviction ideas (3+ funds)
"""

import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

from data.fund_holdings import (
    FUNDS,
    get_all_holdings,
    get_quarter_holdings,
    compute_changes,
    get_cross_fund_holdings,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


# ─── Helpers ──────────────────────────────────────────────

def fmt_val(v):
    if v >= 1e9:
        return f"${v / 1e9:.1f}B"
    return f"${v / 1e6:.0f}M"


def fmt_num(n):
    return f"{n:,}"


def get_latest_quarter():
    df = get_all_holdings()
    return sorted(df["quarter"].unique(), reverse=True)[0]


def fund_keyboard():
    """Inline keyboard with fund buttons."""
    buttons = [
        [InlineKeyboardButton(info["short_name"], callback_data=f"fund_{info['short_name']}")]
        for _, info in FUNDS.items()
    ]
    return InlineKeyboardMarkup(buttons)


def changes_keyboard():
    """Inline keyboard for changes view."""
    buttons = [
        [InlineKeyboardButton(info["short_name"], callback_data=f"changes_{info['short_name']}")]
        for _, info in FUNDS.items()
    ]
    return InlineKeyboardMarkup(buttons)


# ─── Commands ─────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 *13F Fund Tracker Bot*\n\n"
        "Track 13F filings from top institutional investors\\.\n\n"
        "*Commands:*\n"
        "/overview — All funds summary\n"
        "/fund — Deep dive into a fund\n"
        "/changes — Quarter\\-over\\-quarter changes\n"
        "/crossfund — Stocks held by multiple funds\n"
        "/conviction — High\\-conviction ideas \\(3\\+ funds\\)\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)


async def cmd_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = get_latest_quarter()
    df = get_quarter_holdings(q)

    lines = [f"📊 *Portfolio Overview — {q}*\n"]
    for fund_name, info in FUNDS.items():
        fd = df[df["fund"] == fund_name]
        total = fd["value_usd"].sum()
        n = fd["ticker"].nunique()
        top = fd.nlargest(1, "value_usd").iloc[0]
        lines.append(
            f"*{info['short_name']}* — {fmt_val(total)}\n"
            f"  {n} positions · Top: {top['ticker']} ({top['pct_portfolio']:.1f}%)"
        )

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def cmd_fund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        short = context.args[0].upper()
        await send_fund_detail(update.message, short)
    else:
        await update.message.reply_text(
            "Select a fund:", reply_markup=fund_keyboard()
        )


async def send_fund_detail(target, short_name):
    fund_name = None
    for name, info in FUNDS.items():
        if info["short_name"].upper() == short_name.upper():
            fund_name = name
            break

    if not fund_name:
        await target.reply_text(f"Fund '{short_name}' not found. Use /fund to see options.")
        return

    q = get_latest_quarter()
    df = get_quarter_holdings(q)
    fd = df[df["fund"] == fund_name].sort_values("value_usd", ascending=False)
    total = fd["value_usd"].sum()
    info = FUNDS[fund_name]

    lines = [
        f"🏦 *{info['short_name']} — {q}*",
        f"_{info['description']}_\n",
        f"AUM: *{fmt_val(total)}* · {fd['ticker'].nunique()} positions\n",
        "```",
        f"{'Ticker':<8}{'Value':>10}{'  %':>6}",
        "-" * 24,
    ]

    for _, h in fd.iterrows():
        lines.append(f"{h['ticker']:<8}{fmt_val(h['value_usd']):>10}{h['pct_portfolio']:>5.1f}%")

    lines.append("```")
    await target.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def cmd_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        short = context.args[0].upper()
        await send_changes_detail(update.message, short)
    else:
        await update.message.reply_text(
            "Select a fund to see changes:", reply_markup=changes_keyboard()
        )


async def send_changes_detail(target, short_name):
    fund_name = None
    for name, info in FUNDS.items():
        if info["short_name"].upper() == short_name.upper():
            fund_name = name
            break

    if not fund_name:
        await target.reply_text(f"Fund '{short_name}' not found.")
        return

    df = get_all_holdings()
    quarters = sorted(df["quarter"].unique(), reverse=True)
    if len(quarters) < 2:
        await target.reply_text("Need 2+ quarters for changes.")
        return

    changes = compute_changes(fund_name, quarters[0], quarters[1])
    info = FUNDS[fund_name]

    new = changes[changes["action"] == "New Position"]
    increased = changes[changes["action"] == "Increased"]
    reduced = changes[changes["action"] == "Reduced"]
    sold = changes[changes["action"] == "Sold Out"]

    lines = [
        f"📈 *{info['short_name']} Changes: {quarters[1]} → {quarters[0]}*\n",
        f"🟢 New: {len(new)} · ⬆️ Increased: {len(increased)}",
        f"🔴 Reduced: {len(reduced)} · ⬛ Sold: {len(sold)}\n",
    ]

    if len(new) > 0:
        lines.append("*New Positions:*")
        for _, r in new.iterrows():
            lines.append(f"  🟢 {r['ticker']} — {fmt_val(r['curr_value'])}")
        lines.append("")

    if len(increased) > 0:
        lines.append("*Increased:*")
        for _, r in increased.iterrows():
            lines.append(f"  ⬆️ {r['ticker']} +{r['share_change_pct']:.1f}%")
        lines.append("")

    if len(reduced) > 0:
        lines.append("*Reduced:*")
        for _, r in reduced.iterrows():
            lines.append(f"  ⬇️ {r['ticker']} {r['share_change_pct']:.1f}%")
        lines.append("")

    if len(sold) > 0:
        lines.append("*Sold Out:*")
        for _, r in sold.iterrows():
            lines.append(f"  ⬛ {r['ticker']} — was {fmt_val(r['prev_value'])}")

    await target.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def cmd_crossfund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = get_latest_quarter()
    cross = get_cross_fund_holdings(q)
    shared = cross[cross["num_funds"] >= 2].sort_values(
        ["num_funds", "total_value"], ascending=[False, False]
    )

    lines = [f"🔗 *Cross-Fund Holdings — {q}*\n"]
    for _, s in shared.iterrows():
        emoji = "🔥" if s["num_funds"] >= 3 else "🔗"
        lines.append(
            f"{emoji} *{s['ticker']}* — {s['num_funds']} funds\n"
            f"   {s['company']} · {fmt_val(s['total_value'])}\n"
            f"   _{s['funds']}_"
        )

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def cmd_conviction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = get_latest_quarter()
    cross = get_cross_fund_holdings(q)
    high = cross[cross["num_funds"] >= 3].sort_values("num_funds", ascending=False)

    df = get_quarter_holdings(q)

    lines = [
        f"🔥 *High-Conviction Ideas — {q}*",
        "_Stocks held by 3+ tracked funds_\n",
    ]

    if high.empty:
        lines.append("No stocks held by 3+ funds this quarter.")
    else:
        for _, s in high.iterrows():
            lines.append(f"━━━ *{s['ticker']}* — {s['company']} ━━━")
            lines.append(f"Funds: {s['num_funds']} · Total: {fmt_val(s['total_value'])}\n")

            # Show each fund's weight
            ticker_data = df[df["ticker"] == s["ticker"]]
            for _, td in ticker_data.iterrows():
                bar_len = int(td["pct_portfolio"] / 2)
                bar = "█" * bar_len + "░" * (10 - bar_len)
                lines.append(f"  {td['fund_short']:<10} {bar} {td['pct_portfolio']:.1f}%")
            lines.append("")

    lines.append(
        "_These are research starting points where multiple respected "
        "investors hold high-conviction positions. Always do your own DD._"
    )
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


# ─── Callback Handler (inline keyboard) ──────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("fund_"):
        short = data.replace("fund_", "")
        await send_fund_detail(query.message, short)
    elif data.startswith("changes_"):
        short = data.replace("changes_", "")
        await send_changes_detail(query.message, short)


# ─── Main ─────────────────────────────────────────────────

def main():
    if not TOKEN:
        print("=" * 60)
        print("  TELEGRAM BOT TOKEN NOT SET")
        print()
        print("  1. Talk to @BotFather on Telegram")
        print("  2. Create a new bot with /newbot")
        print("  3. Copy the token and run:")
        print()
        print("  export TELEGRAM_BOT_TOKEN='your-token-here'")
        print("  python telegram_bot.py")
        print("=" * 60)
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("overview", cmd_overview))
    app.add_handler(CommandHandler("fund", cmd_fund))
    app.add_handler(CommandHandler("changes", cmd_changes))
    app.add_handler(CommandHandler("crossfund", cmd_crossfund))
    app.add_handler(CommandHandler("conviction", cmd_conviction))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot started. Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
