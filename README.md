# DorkBuilderBot 🤖

A Telegram bot that helps OSINT researchers and security analysts generate advanced Google dork queries across multiple search engines like Google, Bing, Qwant, DuckDuckGo, Yandex, and Mojeek.

## 🔍 Features

- Interactive Telegram conversation to build search queries
- Supports fields like:
  - site / exclude site
  - filetype, inurl, intitle, intext
  - language, location, source
  - Google-style date range conversion
- Outputs manual links ready to open in different engines

## 🚀 Usage

1. Clone the repo or download the script:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dork-builder-bot.git

✅ README.md
markdown
Copy
Edit
# DorkBuilderBot 🤖

A Telegram bot that helps OSINT researchers and security analysts generate advanced Google dork queries across multiple search engines like Google, Bing, Qwant, DuckDuckGo, Yandex, and Mojeek.

## 🔍 Features

- Interactive Telegram conversation to build search queries
- Supports fields like:
  - site / exclude site
  - filetype, inurl, intitle, intext
  - language, location, source
  - Google-style date range conversion
- Outputs manual links ready to open in different engines

## 🚀 Usage

1. Clone the repo or download the script:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dork-builder-bot.git
Install requirements:

bash
Copy
Edit
pip install -r requirements.txt
Run the bot:

In a terminal:

bash
Copy
Edit
python dork_builder_bot.py
Or inside a Jupyter notebook (with nest_asyncio patching).

Start a chat with your bot on Telegram using the /start command.

🛠 Setup
Create a bot using BotFather and get your API token.

Replace the placeholder TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" in the code with your actual token.

📦 Dependencies
python-telegram-bot

nest_asyncio

urllib

datetime

🕵️‍♂️ Use Case Examples
intitle:"index of" site:.gov filetype:pdf

site:pastebin.com intext:password OR leak

filetype:xls inurl:email source:nytimes after:2024-01-01

📜 License
MIT — free to use and modify. Contributions welcome!

yaml
Copy
Edit

