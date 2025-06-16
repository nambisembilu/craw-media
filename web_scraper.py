import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse, urljoin, quote_plus

def is_javascript_site(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        html = res.text.lower()

        # Deteksi pola HTML kosong + JS SPA
        if (
            "<script" in html and (
                "<div id=\"root\"" in html or
                "<app-root" in html or
                "data-reactroot" in html or
                "window.__" in html
            )
        ) and len(html) < 15000:
            return True
    except:
        pass
    return False

def scrape_search_results(base_url, keyword, max_pages=10):
    from playwright.sync_api import sync_playwright

    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    is_js_site = is_javascript_site(base_url)

    if is_js_site:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for page_num in range(1, max_pages + 1):
                if "{parameter}" in base_url:
                    search_url = base_url.replace("{parameter}", quote_plus(keyword))
                else:
                    if "?" in base_url:
                        search_url = f"{base_url}&page={page_num}"
                    else:
                        search_url = f"{base_url}?q={quote_plus(keyword)}&page={page_num}"

                try:
                    page.goto(search_url, timeout=60000)
                    page.wait_for_timeout(3000)
                    anchors = page.query_selector_all("a")
                    for a in anchors:
                        text = a.inner_text().strip()
                        href = a.get_attribute("href")
                        if keyword.lower() in text.lower() and href:
                            results.append({
                                "title": text,
                                "url": href if href.startswith("http") else urljoin(base_url, href),
                                "content": "[Konten tidak diambil di JS mode]"
                            })
                except Exception as e:
                    results.append({
                        "title": f"[Error on {search_url}]",
                        "url": search_url,
                        "content": str(e)
                    })

            browser.close()

    else:
        parsed = urlparse(base_url)
        base_query = parse_qs(parsed.query)
        base_query = {k: v[0] for k, v in base_query.items()}
        base_query = {k: v for k, v in base_query.items() if k != 'page'}

        if 'q' in base_query or 's' not in base_query:
            base_query['q'] = keyword
        else:
            base_query['s'] = keyword

        for page_num in range(1, max_pages + 1):
            query_with_page = {**base_query, "page": page_num}
            new_query = urlencode(query_with_page)
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
                    "title": f"[Error fetching {search_url}]",
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

            if found_links == 0:
                break

    return results
