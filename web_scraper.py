import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def scrape_search_results(base_url, keyword):
    try:
        # Gabungkan keyword ke URL
        if "{parameter}" in base_url:
            search_url = base_url.replace("{parameter}", quote_plus(keyword))
        else:
            search_url = base_url + quote_plus(keyword)

        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(search_url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        results = []
        for link in soup.find_all('a'):
            text = link.text.strip()
            href = link.get('href')
            if keyword.lower() in text.lower() and href:
                results.append({
                    'title': text,
                    'url': href if href.startswith('http') else base_url.rstrip("/") + "/" + href.lstrip("/")
                })
        return results
    except Exception as e:
        return [{'title': f'Error scraping {base_url}', 'url': str(e)}]
