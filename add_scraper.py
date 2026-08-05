with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# We will insert a helper function for web search/scraping and update chat_api
scraper_helper = """
def fetch_deeni_reference(query):
    try:
        import requests
        from bs4 import BeautifulSoup
        # Example search or lookup logic from authentic sources
        # For demonstration, we can query a search or use requests to fetch info
        headers = {'User-Agent': 'Mozilla/5.0'}
        search_url = f"https://html.duckduckgo.com/html/?q={query}+site:darulifta-deoband.com"
        res = requests.get(search_url, headers=headers, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            results = []
            for a in soup.find_all('a', class_='result__snippet', limit=2):
                results.append(a.get_text())
            if results:
                return " | ".join(results)
    except Exception as e:
        print("Scraping error:", e)
    return ""
"""

if "def fetch_deeni_reference" not in code:
    code = scraper_helper + "\n\n" + code
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: Scraper helper added to app.py!")
else:
    print("Scraper helper already exists.")
