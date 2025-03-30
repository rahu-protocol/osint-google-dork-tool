#!/usr/bin/env python
# coding: utf-8

# In[32]:


import urllib.parse
from datetime import datetime, timedelta

USE_INTERACTIVE = True

STATIC_PARAMS = {
    "term": "admin login",
    "site": "",
    "exclude_site": "",
    "related": False,
    "info": False,
    "filetype": "",
    "inurl": "",
    "intitle": "",
    "intext": "",
    "lang": "",
    "location": "",
    "source": "",
    "daterange": "",
    "extra": ""
}

def get_user_input():
    print("\nAnswer the following prompts (press Enter to skip a field):")
    return {
        "term": input("Search term (e.g., 'Tesla stocks', 'climate report'): ") or "",
        "site": input("Specific site (e.g., example.com): ") or "",
        "exclude_site": input("Exclude any specific sites? (e.g., pinterest.com): ") or "",
        "related": input("Want related sites? (y/n) — returns sites similar to the one above: ").lower() == 'y',
        "info": input("Want site info? (y/n) — returns indexing info: ").lower() == 'y',
        "filetype": input("File type (e.g., pdf, xls, docx, sql): ") or "",
        "inurl": input("Keyword in URL (e.g., 'login', 'report'): ") or "",
        "intitle": input("Keyword in title (e.g., 'dashboard', 'leak'): ") or "",
        "intext": input("Keyword in page text (e.g., 'confidential', 'username'): ") or "",
        "lang": input("Language code (e.g., en, fr, es — for Google): ") or "",
        "location": input("Location code (e.g., us, uk, ca — for Bing): ") or "",
        "source": input("News source (e.g., cnn, nytimes — for Google News): ") or "",
        "daterange": input("Date range (Google only, e.g., 'past year', 'past month'): ") or "",
        "extra": input("Extra raw dork terms (e.g., '+secure -site:pinterest.com'): ") or ""
    }

def convert_daterange_to_after(daterange):
    today = datetime.today()
    if "month" in daterange:
        delta = timedelta(days=30)
    elif "year" in daterange:
        delta = timedelta(days=365)
    else:
        return ""
    return (today - delta).strftime("%Y-%m-%d")

def build_full_google_dork(params):
    q = f'"{params["term"]}"'
    if params.get("site"):
        q += f" site:{params['site']}"
    if params.get("exclude_site"):
        q += f" -site:{params['exclude_site']}"
    if params.get("related") and params.get("site"):
        q += f" related:{params['site']}"
    if params.get("info") and params.get("site"):
        q += f" info:{params['site']}"
    if params.get("filetype"):
        q += f" filetype:{params['filetype']}"
    if params.get("inurl"):
        q += f" inurl:{params['inurl']}"
    if params.get("intitle"):
        q += f" intitle:{params['intitle']}"
    if params.get("intext"):
        q += f" intext:{params['intext']}"
    if params.get("lang"):
        q += f" lang:{params['lang']}"
    if params.get("source"):
        q += f" source:{params['source']}"
    if params.get("daterange"):
        date_str = convert_daterange_to_after(params['daterange'])
        if date_str:
            q += f" after:{date_str}"
    if params.get("extra"):
        q += f" {params['extra']}"
    return q.strip()

def build_engine_query(params, engine):
    term = f'"{params.get("term", "")}"'
    site = params.get("site", "")
    q = term
    if site:
        q += f" site:{site}"
    if params.get("exclude_site"):
        q += f" -site:{params['exclude_site']}"
    if params.get("filetype"):
        q += f" filetype:{params['filetype']}"
    if params.get("inurl"):
        q += f" inurl:{params['inurl']}"
    if params.get("intitle"):
        q += f" intitle:{params['intitle']}"
    if params.get("intext"):
        q += f" intext:{params['intext']}"
    if engine == "Bing" and params.get("location"):
        q += f" location:{params['location']}"
    if params.get("extra"):
        q += f" {params['extra']}"
    return q.strip()

def main():
    if USE_INTERACTIVE:
        try:
            params = get_user_input()
        except Exception as e:
            print(f"Error reading input. Falling back to static mode. ({e})")
            params = STATIC_PARAMS
    else:
        params = STATIC_PARAMS

    dork = build_full_google_dork(params)
    print("\nConstructed Dork for Google:\n")
    print(dork + "\n")

    print("Manual links you can open:")
    print("- Google: https://www.google.com/search?q=" + urllib.parse.quote(dork))
    print("- Qwant: https://www.qwant.com/?q=" + urllib.parse.quote(dork))
    print("- Yandex: https://yandex.com/search/?text=" + urllib.parse.quote(dork))

    for engine in ["Bing", "Mojeek", "DuckDuckGo"]:
        query = build_engine_query(params, engine)
        if engine == "Bing":
            url = "https://www.bing.com/search?q=" + urllib.parse.quote(query)
        elif engine == "Mojeek":
            url = "https://www.mojeek.com/search?q=" + urllib.parse.quote(query)
        elif engine == "DuckDuckGo":
            url = "https://duckduckgo.com/?q=" + urllib.parse.quote(query)
        print(f"- {engine}: {url}")

if __name__ == "__main__":
    main()


# In[33]:


get_ipython().system('jupyter nbconvert --to script Dorking_Tool.ipynb')


# In[ ]:




