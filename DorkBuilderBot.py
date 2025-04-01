import nest_asyncio
nest_asyncio.apply()
import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
import urllib.parse
from datetime import datetime, timedelta
import logging

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Your Telegram bot token
TOKEN = "INSERT_TELEGRAM_KEY"

# Steps
(TERM, SITE, EXCLUDE, FILETYPE, INURL, INTITLE, INTEXT, SOURCE, LANG, LOC, DATERANGE, EXTRA) = range(12)

# Convert user-friendly daterange to "after:" date
def convert_daterange_to_after(daterange):
    today = datetime.today()
    if "month" in daterange:
        return (today - timedelta(days=30)).strftime("%Y-%m-%d")
    elif "year" in daterange:
        return (today - timedelta(days=365)).strftime("%Y-%m-%d")
    return ""

# Build per-engine dorks
def build_engine_dork(params, engine):
    terms = params.get("terms", [])
    base = " ".join([f'"{term}"' for term in terms])
    dork = base

    if params.get("site"):
        dork += f" site:{params['site']}"
    if params.get("exclude_sites"):
        for ex in params["exclude_sites"]:
            dork += f" -site:{ex}"
    if params.get("filetype"): dork += f" filetype:{params['filetype']}"
    if params.get("inurl"): dork += f" inurl:{params['inurl']}"
    if params.get("intitle"): dork += f" intitle:{params['intitle']}"
    if params.get("intext"): dork += f" intext:{params['intext']}"
    if params.get("extra"): dork += f" {params['extra']}"

    if engine == "Google":
        if params.get("source"): dork += f" source:{params['source']}"
        if params.get("lang"): dork += f" lang:{params['lang']}"
        if params.get("daterange"):
            after = convert_daterange_to_after(params['daterange'])
            if after: dork += f" after:{after}"
    elif engine == "Bing":
        if params.get("source"): dork += f" source:{params['source']}"
        if params.get("loc"): dork += f" location:{params['loc']}"
    elif engine == "Yandex":
        if params.get("lang"): dork += f" lang:{params['lang']}"
        if params.get("loc"): dork += f" location:{params['loc']}"

    return dork.strip()

# ---- Step Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['terms'] = []
    context.user_data['exclude_sites'] = []
    await update.message.reply_text("Welcome to DorkBuilderBot! 🕵️‍♂️\n\nEnter a keyword or phrase. Type 'done' when finished.")
    return TERM

async def ask_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() == "done":
        await update.message.reply_text("Specific site? (example.com or type 'skip')")
        return SITE
    context.user_data['terms'].append(text)
    await update.message.reply_text("Add another keyword or type 'done'")
    return TERM

async def ask_site(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data['site'] = "" if text.lower() == "skip" else text
    await update.message.reply_text("Exclude any site? Enter one at a time and type 'done' when finished.")
    return EXCLUDE

async def ask_exclude(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() == "done":
        await update.message.reply_text("File type? (e.g., pdf, xls or 'skip')")
        return FILETYPE
    context.user_data['exclude_sites'].append(text)
    await update.message.reply_text("Add another site to exclude or type 'done'")
    return EXCLUDE

async def ask_step(update: Update, context: ContextTypes.DEFAULT_TYPE, key, prompt, next_step):
    text = update.message.text.strip()
    context.user_data[key] = "" if text.lower() == "skip" else text
    await update.message.reply_text(prompt)
    return next_step

async def ask_filetype(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "filetype", "Keyword in URL? (or 'skip')", INURL)

async def ask_inurl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "inurl", "Keyword in Title? (or 'skip')", INTITLE)

async def ask_intitle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "intitle", "Keyword in Page Text? (or 'skip')", INTEXT)

async def ask_intext(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "intext", "News Source? (or 'skip')", SOURCE)

async def ask_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "source", "Language Code? (or 'skip')", LANG)

async def ask_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "lang", "Location Code? (or 'skip')", LOC)

async def ask_loc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "loc", "Date range? (past month, year, etc — or 'skip')", DATERANGE)

async def ask_daterange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "daterange", "Any extra raw dork terms? (or 'skip')", EXTRA)

async def ask_extra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['extra'] = update.message.text.strip() if update.message.text.lower() != "skip" else ""
    links = []

    for engine, base_url in {
        "Google": "https://www.google.com/search?q=",
        "Qwant": "https://www.qwant.com/?q=",
        "Yandex": "https://yandex.com/search/?text=",
        "Bing": "https://www.bing.com/search?q=",
        "Mojeek": "https://www.mojeek.com/search?q=",
        "DuckDuckGo": "https://duckduckgo.com/?q="
    }.items():
        dork = build_engine_dork(context.user_data, engine)
        encoded = urllib.parse.quote(dork)
        links.append(f"[{engine}]({base_url}{encoded})")

    message = f"""🔎 *Constructed Dork*:
`{build_engine_dork(context.user_data, 'Google')}`

🌐 *Manual Links*:
{chr(10).join(links)}"""

    await update.message.reply_text(message, parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Search cancelled.")
    return ConversationHandler.END

# ---- Run Bot ----
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TERM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_term)],
            SITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_site)],
            EXCLUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_exclude)],
            FILETYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_filetype)],
            INURL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_inurl)],
            INTITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_intitle)],
            INTEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_intext)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_source)],
            LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_lang)],
            LOC: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_loc)],
            DATERANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_daterange)],
            EXTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_extra)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv)
    await app.initialize()
    await app.start()
    print("🤖 Bot is running in Jupyter...")
    await app.updater.start_polling()

# If in Jupyter, launch as task
if __name__ == "__main__":
    if 'get_ipython' in globals():
        asyncio.get_event_loop().create_task(run_bot())
    else:
        asyncio.run(run_bot())
