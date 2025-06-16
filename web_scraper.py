import requests
from bs4 import BeautifulSoup

def scrape_search_results(url, keyword):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        results = []
        for link in soup.find_all('a'):
            text = link.text.strip()
            href = link.get('href')
            if keyword.lower() in text.lower() and href:
                results.append({
                    'title': text,
                    'url': href if href.startswith('http') else url + href
                })
        return results
    except Exception as e:
        return [{'title': f'Error scraping {url}', 'url': str(e)}]