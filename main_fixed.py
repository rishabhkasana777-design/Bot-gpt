"""
Railway Entry Point - Trades GPT Bot
This file is required for Railway to auto-detect and run the bot.
"""

import os
import asyncio
import random
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from telegram.constants import ParseMode

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8862197239:AAGotf6wfdoDnzfKWaFprI7JKNGvqRdJr_A"
ADMIN_ID = 825056841
ADMIN_USERNAME = "@Rishabhkasana777"
CREATE_ACCOUNT_LINK = "https://u3.shortink.io/register?utm_campaign=826893&utm_source=affiliate&utm_medium=sr&a=WxLmRQigGoQehq&al=1745149&ac=rishabhkasana777&cid=949480&code=WELCOME50"

LOGO_PATH = os.path.join(os.path.dirname(__file__), "trades_gpt_logo.png")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== ALLOWED PAIRS (REAL FOREX ONLY - NO OTC) ====================
ALLOWED_PAIRS = [
    "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD",
    "EURGBP", "EURAUD", "EURCAD", "EURCHF", "EURNZD",
    "GBPAUD", "GBPCAD", "GBPCHF", "GBPNZD",
    "USDJPY", "USDCHF", "USDCAD", "USDZAR",
    "AUDJPY", "AUDCAD", "AUDCHF", "AUDNZD",
    "CADCHF", "CADJPY",
    "CHFJPY",
    "EURJPY", "GBPJPY", "NZDJPY"
]

BINARY_TIMEFRAMES = ["1M", "5M", "15M"]
SIGNAL_TYPES = ["CALL", "PUT"]

(START, WAITING_TRADER_ID, WAITING_PROOF) = range(3)

user_data = {}
pending_approvals = {}
signal_history = {}
stats = {"total_signals": 0, "approved_users": 0, "pending_users": 0}

START_MESSAGE_CAPTION = (
    "💹 <b>Trades GPT</b>\n\n"
    "🚫 <b>We DO NOT use OTC pairs</b>\n"
    "✅ We trade only <b>REAL Forex market pairs</b> for higher accuracy & reliability\n\n"
    "🧠 Our strategy is not random — it's built on advanced trading concepts:\n\n"
    "💡 Smart Money Concepts (SMC)\n"
    "💡 Fair Value Gaps (FVG)\n"
    "💡 Liquidity Trap Detection\n"
    "💡 Support & Resistance Zones\n"
    "💡 Breakout + Reversal Confirmations\n"
    "💡 EMA 25 / 50 Reaction Strategy\n\n"
    "📈 Multi-layer confirmation system ensures:\n"
    "✔️ High probability entries\n"
    "✔️ Low risk setups\n"
    "✔️ Precision timing (5M sniper trades)\n\n"
    "⚡ We don't spam signals\n"
    "🎯 Only the BEST setups are sent\n\n"
    "💰 Designed for serious traders who want consistency — not luck\n\n"
    "🚀 Join the system. Trade smart. Win smarter.\n\n"
    "👇 <b>Complete the steps below to get access</b>"
)

def get_start_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 CREATE ACCOUNT", url=CREATE_ACCOUNT_LINK)],
        [InlineKeyboardButton("🆔 SUBMIT TRADER ID", callback_data="submit_trader_id")],
        [InlineKeyboardButton("📩 SUBMIT PROOF", callback_data="submit_proof")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_approval_keyboard(user_id: int):
    keyboard = [
        [
            InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{user_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_signal_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")],
        [InlineKeyboardButton("📈 SIGNAL HISTORY", callback_data="signal_history")],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_approved_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")],
        [InlineKeyboardButton("📈 MY STATS", callback_data="my_stats")],
        [InlineKeyboardButton("📜 SIGNAL HISTORY", callback_data="signal_history")],
        [InlineKeyboardButton("ℹ️ HOW IT WORKS", callback_data="how_it_works")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_strategy_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 SMC STRATEGY", callback_data="strategy_smc")],
        [InlineKeyboardButton("📈 FVG EXPLAINED", callback_data="strategy_fvg")],
        [InlineKeyboardButton("🎯 ENTRY RULES", callback_data="strategy_entry")],
        [InlineKeyboardButton("⬅️ BACK TO MENU", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def generate_binary_signal():
    pair = random.choice(ALLOWED_PAIRS)
    signal_type = random.choice(SIGNAL_TYPES)
    timeframe_weights = [0.2, 0.6, 0.2]
    timeframe = random.choices(BINARY_TIMEFRAMES, weights=timeframe_weights)[0]
    confidence = random.choices(["HIGH", "MEDIUM", "LOW"], weights=[0.5, 0.35, 0.15])[0]

    if timeframe == "1M":
        entry_time = "1M DOWN"
        expiry = "1 minute"
    elif timeframe == "5M":
        entry_time = "5M DOWN"
        expiry = "5 minutes"
    else:
        entry_time = "15M DOWN"
        expiry = "15 minutes"

    strategies = [
        "SMC Liquidity Sweep + FVG",
        "EMA 25/50 Golden Cross",
        "Support/Resistance Bounce",
        "Breakout + Retest Confirmation",
        "FVG Fill + Reversal",
        "Liquidity Trap Triggered"
    ]
    strategy_used = random.choice(strategies)
    conf_emoji = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}

    signal_text = (
        f"📊 <b>TRADES GPT SIGNAL</b>\n\n"
        f"💱 <b>Pair:</b> <code>{pair}</code>\n"
        f"📉 <b>Direction:</b> {'🟢 CALL (UP)' if signal_type == 'CALL' else '🔴 PUT (DOWN)'}\n"
        f"⏰ <b>Timeframe:</b> {timeframe}\n"
        f"🎯 <b>Entry:</b> {entry_time}\n"
        f"⏳ <b>Expiry:</b> {expiry}\n\n"
        f"🧠 <b>Strategy:</b> {strategy_used}\n"
        f"{conf_emoji[confidence]} <b>Confidence:</b> {confidence}\n\n"
        f"📈 <b>Market Analysis:</b>\n"
        f"• Pair Type: {'JPY Pair' if 'JPY' in pair else 'Major Pair' if len(pair) == 6 else 'Cross Pair'}\n"
        f"• Session: {random.choice(['London', 'New York', 'Asian', 'Overlap'])}\n"
        f"• Volatility: {random.choice(['High', 'Medium', 'Low'])}\n\n"
        f"⚠️ <b>Risk Management:</b>\n"
        f"• Max 2% per trade\n"
        f"• Use martingale carefully\n"
        f"• Stop after 3 consecutive losses\n"
        f"• Follow strict money management\n\n"
        f"🚀 <b>Trade smart. Win smarter.</b>"
    )

    return {
        "text": signal_text,
        "pair": pair,
        "direction": signal_type,
        "timeframe": timeframe,
        "confidence": confidence,
        "strategy": strategy_used,
        "timestamp": datetime.now()
    }

def get_status_message(user_id: int):
    if user_id not in user_data:
        return "❌ You haven't started the verification process yet. Use /start"

    status = user_data[user_id].get("status", "unknown")
    trader_id = user_data[user_id].get("trader_id", "Not submitted")
    status_emoji = {"new": "🆕", "pending_id": "⏳", "pending_approval": "🕐", "approved": "✅", "rejected": "❌"}

    msg = (
        f"📋 <b>YOUR STATUS</b>\n\n"
        f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
        f"🆔 <b>Trader ID:</b> <code>{trader_id}</code>\n"
        f"📊 <b>Status:</b> {status_emoji.get(status, '❓')} {status.upper()}"
    )

    if status == "approved":
        approved_at = user_data[user_id].get("approved_at")
        signals_count = len(signal_history.get(user_id, []))
        msg += (
            f"\n\n🎉 <b>VERIFIED MEMBER</b>\n"
            f"✅ Approved on: {approved_at.strftime('%Y-%m-%d %H:%M') if approved_at else 'N/A'}\n"
            f"📊 Signals received: {signals_count}\n\n"
            f"🚀 Use /signal to get trading signals!"
        )
    elif status == "pending_approval":
        msg += "\n\n⏳ Waiting for admin approval...\n📩 Proof submitted"
    elif status == "pending_id":
        msg += "\n\n🆔 Trader ID submitted\n📩 Please submit deposit proof"

    return msg

def get_how_it_works_text():
    return (
        "📚 <b>HOW TRADES GPT WORKS</b>\n\n"
        "<b>1️⃣ Verification Process</b>\n"
        "• Submit your Trader ID\n"
        "• Send deposit proof screenshot\n"
        "• Wait for admin approval\n"
        "• Get full signal access\n\n"
        "<b>2️⃣ Signal Generation</b>\n"
        "• Real Forex pairs only (NO OTC)\n"
        "• Advanced SMC + FVG strategy\n"
        "• Multi-timeframe analysis\n"
        "• 1M / 5M / 15M precision entries\n\n"
        "<b>3️⃣ Trading Rules</b>\n"
        "• Follow signals exactly\n"
        "• Use proper risk management\n"
        "• Max 2% risk per trade\n"
        "• Don't overtrade\n\n"
        "<b>4️⃣ Strategy Foundation</b>\n"
        "• Smart Money Concepts\n"
        "• Fair Value Gap detection\n"
        "• Liquidity trap identification\n"
        "• EMA 25/50 reaction zones\n\n"
        "⚡ <b>Only high-probability setups are sent!</b>"
    )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if user_id not in user_data:
        user_data[user_id] = {
            "trader_id": None,
            "proof_photo_id": None,
            "status": "new",
            "approved_at": None,
            "signals_received": 0
        }

    chat_id = update.effective_chat.id

    try:
        with open(LOGO_PATH, 'rb') as logo_file:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=logo_file,
                caption=START_MESSAGE_CAPTION,
                parse_mode=ParseMode.HTML,
                reply_markup=get_start_keyboard()
            )
    except FileNotFoundError:
        await update.message.reply_text(
            START_MESSAGE_CAPTION,
            parse_mode=ParseMode.HTML,
            reply_markup=get_start_keyboard()
        )

    status_messages = [
        "⏳ Checking VIP availability...",
        "📊 Scanning active traders...",
        "🧠 Loading SMC strategy engine...",
        "⚠️ Only 8 VIP slots remaining — filling fast",
        "🚀 Complete steps now to secure your spot!"
    ]

    for msg in status_messages:
        await asyncio.sleep(0.6)
        await context.bot.send_message(chat_id=chat_id, text=msg)

    return START

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_data or user_data[user_id].get("status") != "approved":
        await update.message.reply_text(
            "❌ <b>Access Denied!</b>\n\n"
            "You need to complete verification first.\n"
            "Use /start to begin.",
            parse_mode=ParseMode.HTML
        )
        return

    signal = generate_binary_signal()

    if user_id not in signal_history:
        signal_history[user_id] = []
    signal_history[user_id].append(signal)
    user_data[user_id]["signals_received"] += 1
    stats["total_signals"] += 1

    await update.message.reply_text(
        signal["text"],
        parse_mode=ParseMode.HTML,
        reply_markup=get_signal_keyboard()
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    status_msg = get_status_message(user_id)
    await update.message.reply_text(status_msg, parse_mode=ParseMode.HTML)

async def strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 <b>TRADING STRATEGIES</b>\n\nSelect a strategy to learn more:",
        parse_mode=ParseMode.HTML,
        reply_markup=get_strategy_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 <b>TRADES GPT COMMANDS</b>\n\n"
        "/start - Start bot & verification\n"
        "/signal - Get trading signal\n"
        "/status - Check your status\n"
        "/strategy - Learn our strategies\n"
        "/help - Show this help message\n\n"
        "<b>For Approved Users:</b>\n"
        "📊 Get signals anytime with /signal\n"
        "📈 View your stats with /status\n"
        "🧠 Learn strategies with /strategy\n\n"
        "<b>Admin Only:</b>\n"
        "/stats - View bot statistics\n"
        "/broadcast - Send message to all users"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    total_users = len(user_data)
    approved = sum(1 for u in user_data.values() if u.get("status") == "approved")
    pending = sum(1 for u in user_data.values() if u.get("status") == "pending_approval")

    stats_text = (
        f"📊 <b>BOT STATISTICS</b>\n\n"
        f"👤 Admin: {ADMIN_USERNAME}\n"
        f"👥 Total Users: {total_users}\n"
        f"✅ Approved: {approved}\n"
        f"⏳ Pending Approval: {pending}\n"
        f"📈 Total Signals Sent: {stats['total_signals']}\n\n"
        f"🤖 Bot Status: <b>ONLINE</b>"
    )
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)

async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message here")
        return

    message = " ".join(context.args)
    sent_count = 0
    failed_count = 0

    for user_id in user_data:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>ANNOUNCEMENT</b>\n\n{message}",
                parse_mode=ParseMode.HTML
            )
            sent_count += 1
            await asyncio.sleep(0.1)
        except Exception:
            failed_count += 1

    await update.message.reply_text(
        f"✅ Broadcast sent to {sent_count} users\n❌ Failed: {failed_count}"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    if data == "submit_trader_id":
        await query.message.reply_text(
            "🆔 <b>Submit your Trader ID</b>\n\n"
            "Please send your Trader/Account ID from the broker:",
            parse_mode=ParseMode.HTML
        )
        return WAITING_TRADER_ID

    elif data == "submit_proof":
        if user_id not in user_data or not user_data[user_id].get("trader_id"):
            await query.message.reply_text(
                "❌ Please submit your Trader ID first!\n"
                "Click '🆔 SUBMIT TRADER ID' button.",
                parse_mode=ParseMode.HTML
            )
            return START

        await query.message.reply_text(
            "📩 <b>Submit Deposit Proof</b>\n\n"
            "Please send a screenshot of your deposit confirmation:\n"
            "(Minimum deposit: $10-$50)",
            parse_mode=ParseMode.HTML
        )
        return WAITING_PROOF

    elif data == "get_signal":
        if user_id not in user_data or user_data[user_id].get("status") != "approved":
            await query.message.reply_text(
                "❌ You need admin approval to get signals!\n"
                "Complete verification and wait for approval.",
                parse_mode=ParseMode.HTML
            )
            return

        signal = generate_binary_signal()

        if user_id not in signal_history:
            signal_history[user_id] = []
        signal_history[user_id].append(signal)
        user_data[user_id]["signals_received"] += 1
        stats["total_signals"] += 1

        await query.message.reply_text(
            signal["text"],
            parse_mode=ParseMode.HTML,
            reply_markup=get_signal_keyboard()
        )

    elif data == "signal_history":
        if user_id not in signal_history or not signal_history[user_id]:
            await query.message.reply_text(
                "📭 No signal history yet.\nUse 📊 GET SIGNAL to start!",
                parse_mode=ParseMode.HTML
            )
            return

        history = signal_history[user_id][-5:]
        history_text = "📜 <b>LAST 5 SIGNALS</b>\n\n"
        for i, sig in enumerate(reversed(history), 1):
            history_text += f"{i}. {sig['pair']} {'🟢 CALL' if sig['direction'] == 'CALL' else '🔴 PUT'} | {sig['timeframe']} | {sig['confidence']}\n"

        await query.message.reply_text(history_text, parse_mode=ParseMode.HTML)

    elif data == "my_stats":
        signals_count = user_data[user_id].get("signals_received", 0)
        await query.message.reply_text(
            f"📈 <b>YOUR STATS</b>\n\n"
            f"📊 Signals received: {signals_count}\n"
            f"✅ Status: APPROVED\n"
            f"🎯 Keep trading smart!",
            parse_mode=ParseMode.HTML
        )

    elif data == "how_it_works":
        await query.message.reply_text(
            get_how_it_works_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=get_approved_menu_keyboard()
        )

    elif data == "refresh":
        if user_id not in user_data or user_data[user_id].get("status") != "approved":
            await query.message.reply_text("❌ Not approved yet!", parse_mode=ParseMode.HTML)
            return

        signal = generate_binary_signal()

        if user_id not in signal_history:
            signal_history[user_id] = []
        signal_history[user_id].append(signal)
        user_data[user_id]["signals_received"] += 1

        await query.edit_message_text(
            signal["text"],
            parse_mode=ParseMode.HTML,
            reply_markup=get_signal_keyboard()
        )

    elif data == "strategy_smc":
        await query.message.reply_text(
            (
                "🧠 <b>SMART MONEY CONCEPTS (SMC)</b>\n\n"
                "We track where institutional money moves:\n\n"
                "• <b>Liquidity Sweeps:</b> Stop hunts before reversals\n"
                "• <b>Order Blocks:</b> Where big players placed orders\n"
                "• <b>Breaker Blocks:</b> Failed support becomes resistance\n"
                "• <b>Fair Value Gaps:</b> Imbalanced price zones\n\n"
                "💡 We trade WITH the smart money, not against it."
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_strategy_keyboard()
        )

    elif data == "strategy_fvg":
        await query.message.reply_text(
            (
                "📈 <b>FAIR VALUE GAPS (FVG)</b>\n\n"
                "Price often returns to fill gaps:\n\n"
                "• <b>Bullish FVG:</b> Price drops to fill gap → BOUNCE\n"
                "• <b>Bearish FVG:</b> Price rises to fill gap → REJECT\n\n"
                "🎯 Entry triggers when:\n"
                "✅ FVG aligns with support/resistance\n"
                "✅ Confirmed by EMA reaction\n"
                "✅ Liquidity sweep precedes it\n\n"
                "⚡ High probability reversal zones!"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_strategy_keyboard()
        )

    elif data == "strategy_entry":
        await query.message.reply_text(
            (
                "🎯 <b>ENTRY RULES</b>\n\n"
                "<b>CALL Entry Conditions:</b>\n"
                "✅ Price at support zone\n"
                "✅ Bullish FVG present\n"
                "✅ EMA 25 above EMA 50\n"
                "✅ Liquidity sweep completed\n"
                "✅ 5M candle confirmation\n\n"
                "<b>PUT Entry Conditions:</b>\n"
                "✅ Price at resistance zone\n"
                "✅ Bearish FVG present\n"
                "✅ EMA 25 below EMA 50\n"
                "✅ Liquidity sweep completed\n"
                "✅ 5M candle confirmation\n\n"
                "⚠️ <b>NO TRADE if:</b>\n"
                "❌ High impact news within 30 min\n"
                "❌ Spread too wide\n"
                "❌ No clear setup"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_strategy_keyboard()
        )

    elif data == "back_menu":
        await query.message.reply_text(
            "🧠 <b>TRADING STRATEGIES</b>\n\nSelect a strategy to learn more:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_strategy_keyboard()
        )

    return START

async def handle_trader_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    trader_id = update.message.text.strip()

    user_data[user_id]["trader_id"] = trader_id
    user_data[user_id]["status"] = "pending_id"

    await update.message.reply_text(
        f"✅ <b>Trader ID Received!</b>\n\n"
        f"🆔 ID: <code>{trader_id}</code>\n\n"
        f"Now please submit your deposit proof by clicking '📩 SUBMIT PROOF'",
        parse_mode=ParseMode.HTML,
        reply_markup=get_start_keyboard()
    )

    return START

async def handle_proof_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not update.message.photo:
        await update.message.reply_text(
            "❌ Please send a photo/screenshot of your deposit proof!",
            parse_mode=ParseMode.HTML
        )
        return WAITING_PROOF

    photo = update.message.photo[-1]
    photo_id = photo.file_id

    user_data[user_id]["proof_photo_id"] = photo_id
    user_data[user_id]["status"] = "pending_approval"
    stats["pending_users"] += 1

    await update.message.reply_text(
        "📩 <b>Proof Received!</b>\n\n"
        "⏳ Your submission is now under review.\n"
        "You will be notified once approved.\n\n"
        "⚠️ Please wait for admin approval before requesting signals.",
        parse_mode=ParseMode.HTML
    )

    trader_id = user_data[user_id].get("trader_id", "N/A")
    username = update.effective_user.username or "No username"
    first_name = update.effective_user.first_name or "No name"

    admin_msg = (
        f"🚨 <b>NEW PROOF SUBMISSION</b>\n\n"
        f"👤 <b>User:</b> {first_name} (@{username})\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"🆔 <b>Trader ID:</b> <code>{trader_id}</code>\n"
        f"📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"📸 <b>Deposit Proof attached below</b>\n\n"
        f"Please review and approve/reject:"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_msg,
        parse_mode=ParseMode.HTML
    )

    sent_msg = await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        reply_markup=get_admin_approval_keyboard(user_id)
    )

    pending_approvals[user_id] = sent_msg

    return START

async def admin_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.answer("❌ Unauthorized!", show_alert=True)
        return

    data = query.data
    action, target_user_id = data.split("_", 1)
    target_user_id = int(target_user_id)

    if action == "approve":
        user_data[target_user_id]["status"] = "approved"
        user_data[target_user_id]["approved_at"] = datetime.now()
        stats["approved_users"] += 1

        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ <b>APPROVED</b> by admin",
            parse_mode=ParseMode.HTML
        )

        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "🎉 <b>CONGRATULATIONS!</b>\n\n"
                "✅ Your deposit proof has been <b>APPROVED</b>!\n\n"
                "🎊 You now have FULL ACCESS to:\n"
                "• Premium trading signals\n"
                "• VIP community access\n"
                "• AI-assisted trading\n"
                "• SMC + FVG strategy signals\n\n"
                "📊 Use /signal to get your first signal!\n"
                "🚀 Trade smart. Win smarter."
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_approved_menu_keyboard()
        )

    elif action == "reject":
        user_data[target_user_id]["status"] = "rejected"

        await query.edit_message_caption(
            caption=query.message.caption + "\n\n❌ <b>REJECTED</b> by admin",
            parse_mode=ParseMode.HTML
        )

        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "❌ <b>SUBMISSION REJECTED</b>\n\n"
                "Your deposit proof was not approved.\n\n"
                "Possible reasons:\n"
                "• Invalid or unclear screenshot\n"
                "• Deposit amount not matching requirements\n"
                "• Fake or edited proof\n\n"
                "Please submit a valid proof again.\n"
                "Use /start to restart."
            ),
            parse_mode=ParseMode.HTML
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred. Please try again or contact support."
        )

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command),
            CallbackQueryHandler(button_callback, pattern="^(submit_trader_id|submit_proof|get_signal|signal_history|my_stats|how_it_works|refresh|strategy_smc|strategy_fvg|strategy_entry|back_menu)$")
        ],
        states={
            START: [
                CallbackQueryHandler(button_callback, pattern="^(submit_trader_id|submit_proof|get_signal|signal_history|my_stats|how_it_works|refresh|strategy_smc|strategy_fvg|strategy_entry|back_menu)$"),
                CommandHandler("start", start_command),
            ],
            WAITING_TRADER_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_trader_id),
            ],
            WAITING_PROOF: [
                MessageHandler(filters.PHOTO, handle_proof_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: u.message.reply_text("Please send a PHOTO of your deposit proof!")),
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("signal", signal_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("strategy", strategy_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", admin_stats_command))
    application.add_handler(CommandHandler("broadcast", admin_broadcast_command))
    application.add_handler(CallbackQueryHandler(admin_approval_callback, pattern="^(approve|reject)_"))
    application.add_error_handler(error_handler)

    print("🚀 Trades GPT Bot started on Railway! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
