import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse, urljoin


def scrape_search_results(base_url, keyword, max_pages=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    # Parse base URL
    parsed = urlparse(base_url)
    base_query = parse_qs(parsed.query)

    # Tambahkan parameter pencarian
    base_query = {k: v[0] for k, v in base_query.items()}
    base_query = {k: v for k, v in base_query.items() if k != 'page'}  # hilangkan page jika ada

    base_query = {**base_query, **{"q": keyword}} if 'q' in base_query or 's' not in base_query else {**base_query, **{"s": keyword}}

    for page in range(1, max_pages + 1):
        # Tambahkan parameter halaman
        query_with_page = {**base_query, "page": page}
        new_query = urlencode(query_with_page)

        # Rekonstruksi URL dengan query baru
        search_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

        try:
            res = requests.get(search_url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
        except Exception as e:
            results.append({
                "title": f"Error fetching {search_url}",
                "url": search_url,
                "content": str(e)
            })
            continue

        found_links = 0
        for link in soup.find_all('a'):
            text = link.text.strip()
            href = link.get('href')
            if keyword.lower() in text.lower() and href:
                found_links += 1
                full_url = href if href.startswith('http') else urljoin(base_url, href)

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

        # Stop jika tidak ditemukan link baru (misal di page 4 sudah kosong)
        if found_links == 0:
            break

    return results
