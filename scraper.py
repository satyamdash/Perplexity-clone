import requests
from boilerpy3 import extractors


def scrape_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        extractor = extractors.ArticleExtractor()
        content = extractor.get_content(response.text)

        return content.strip()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return ""

