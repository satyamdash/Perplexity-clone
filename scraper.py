import requests
from boilerpy3 import extractors


def extract_text_from_url(url):
    extractor = extractors.ArticleExtractor()
    try:
        html = requests.get(url, timeout=10).text
        content = extractor.get_content(html)
        return content
    except Exception as e:
        print(f"[!] Failed to scrape {url}: {e}")
        return ""