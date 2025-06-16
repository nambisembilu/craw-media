import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin

def scrape_search_results(base_url, keyword, max_pages=5):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        results = []
        current_page = 1

        if "{parameter}" in base_url:
            search_url = base_url.replace("{parameter}", quote_plus(keyword))
        else:
            search_url = base_url + quote_plus(keyword)

        while search_url and current_page <= max_pages:
            res = requests.get(search_url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')

            # Ambil semua hasil link yang mengandung keyword
            for link in soup.find_all('a'):
                text = link.text.strip()
                href = link.get('href')
                if keyword.lower() in text.lower() and href:
                    full_url = href if href.startswith('http') else urljoin(base_url, href)

                    # Ambil konten dari halaman
                    content = ""
                    try:
                        subres = requests.get(full_url, headers=headers, timeout=10)
                        subsoup = BeautifulSoup(subres.text, 'html.parser')
                        paragraphs = subsoup.find_all('p')
                        content = " ".join(p.get_text().strip() for p in paragraphs if p.get_text())
                        content = content[:1000]
                    except Exception as sub_e:
                        content = f"[Gagal ambil isi konten: {sub_e}]"

                    results.append({
                        'title': text,
                        'url': full_url,
                        'content': content
                    })

            # Cari link ke halaman berikutnya
            next_link = soup.find('a', string=lambda t: t and ("Next" in t or "Berikutnya" in t or ">" in t))
            if next_link and next_link.get('href'):
                search_url = urljoin(base_url, next_link.get('href'))
                current_page += 1
            else:
                break

        return results

    except Exception as e:
        return [{
            'title': f'Error scraping {base_url}',
            'url': str(e),
            'content': ''
        }]
