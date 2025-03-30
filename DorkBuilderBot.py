#!/usr/bin/env python
# coding: utf-8

# In[2]:


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
import nest_asyncio
import asyncio
import logging

# Enable logging to debug issues
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Apply patch for running asyncio in Jupyter
nest_asyncio.apply()

# Bot token from BotFather
TOKEN = "INSERT_TELEGRAM_API_KEY"

# Conversation steps
(TERM, SITE, EXCLUDE, FILETYPE, INURL, INTITLE, INTEXT, SOURCE, LANG, LOC, DATERANGE, EXTRA) = range(12)

# Function to convert daterange
def convert_daterange_to_after(daterange):
    today = datetime.today()
    if "month" in daterange:
        delta = timedelta(days=30)
    elif "year" in daterange:
        delta = timedelta(days=365)
    else:
        return ""
    return (today - delta).strftime("%Y-%m-%d")

# Build per-engine dorks based on supported keys
def build_engine_dork(params, engine):
    base = f'"{params.get("term", "")}"'
    dork = base
    if params.get("site"): dork += f" site:{params['site']}"
    if params.get("exclude"): dork += f" -site:{params['exclude']}"
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
            if after:
                dork += f" after:{after}"
    elif engine == "Bing":
        if params.get("source"): dork += f" source:{params['source']}"
        if params.get("loc"): dork += f" location:{params['loc']}"
    elif engine == "Yandex":
        if params.get("lang"): dork += f" lang:{params['lang']}"
        if params.get("loc"): dork += f" location:{params['loc']}"

    return dork.strip()

# Step functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome to DorkBuilderBot! 🕵️‍♂️\n\nWhat would you like to search for?")
    return TERM

async def ask_step(update: Update, context: ContextTypes.DEFAULT_TYPE, key, prompt, next_step):
    text = update.message.text.strip()
    context.user_data[key] = "" if text.lower() == "skip" else text
    await update.message.reply_text(prompt)
    return next_step

async def ask_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['term'] = update.message.text
    await update.message.reply_text("Specific site? (example.com or enter 'skip')")
    return SITE

async def ask_site(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "site", "Exclude any site? (e.g., pinterest.com or enter 'skip')", EXCLUDE)

async def ask_exclude(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "exclude", "File type? (e.g., pdf, xls or enter 'skip')", FILETYPE)

async def ask_filetype(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "filetype", "Keyword in URL? (or enter 'skip')", INURL)

async def ask_inurl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "inurl", "Keyword in Title? (or enter 'skip')", INTITLE)

async def ask_intitle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "intitle", "Keyword in Page Text? (or enter 'skip')", INTEXT)

async def ask_intext(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "intext", "News Source? (e.g., cnn or enter 'skip')", SOURCE)

async def ask_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "source", "Language code? (e.g., en, fr — or enter 'skip')", LANG)

async def ask_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "lang", "Location code? (e.g., us, uk — or enter 'skip')", LOC)

async def ask_loc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "loc", "Date range? (past month, past year, or enter 'skip')", DATERANGE)

async def ask_daterange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await ask_step(update, context, "daterange", "Any extra raw dork terms? (or enter 'skip')", EXTRA)

async def ask_extra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['extra'] = update.message.text if update.message.text.lower() != "skip" else ""

    links = []
    for engine, base_url in {
        "Google": "https://www.google.com/search?q=",
        "Qwant": "https://www.qwant.com/?q=",
        "Yandex": "https://yandex.com/search/?text=",
        "Bing": "https://www.bing.com/search?q=",
        "Mojeek": "https://www.mojeek.com/search?q=",
        "DuckDuckGo": "https://duckduckgo.com/?q="
    }.items():
        query = build_engine_dork(context.user_data, engine)
        encoded = urllib.parse.quote(query)
        links.append(f"[{engine}]({base_url}{encoded})")

    combined = "\n".join(links)
    message = f"""🔎 *Constructed Dork*:
`{build_engine_dork(context.user_data, 'Google')}`

🌐 *Manual Links*:
{combined}"""

    await update.message.reply_text(message, parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Search cancelled.")
    return ConversationHandler.END

steps = [ask_term, ask_site, ask_exclude, ask_filetype, ask_inurl, ask_intitle, ask_intext, ask_source, ask_lang, ask_loc, ask_daterange, ask_extra]

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
    logging.info("🤖 Bot is running in Jupyter...")
    await app.updater.start_polling()

ipy = get_ipython()
if ipy:
    asyncio.get_event_loop().create_task(run_bot())
    print("✅ Bot task launched inside Jupyter notebook.")
else:
    asyncio.run(run_bot())


# In[1]:


get_ipython().system('jupyter nbconvert --to script Dorking_Tool.ipynb')


# In[ ]:




