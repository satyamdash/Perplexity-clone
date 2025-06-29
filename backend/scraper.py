import aiohttp
import asyncio
from boilerpy3 import extractors
import requests


async def scrape_url_async(session, url, timeout=5):
    """Async version of scraper with reduced timeout"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
            response.raise_for_status()
            html = await response.text()
            
            extractor = extractors.ArticleExtractor()
            content = extractor.get_content(html)
            return content.strip()
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return ""


async def scrape_urls_parallel(urls, max_concurrent=3):
    """Scrape multiple URLs in parallel"""
    connector = aiohttp.TCPConnector(
        limit=max_concurrent,
        ssl=False,  # Disable SSL verification for now
        limit_per_host=2
    )
    timeout = aiohttp.ClientTimeout(total=5)
    
    async with aiohttp.ClientSession(
        connector=connector, 
        timeout=timeout,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    ) as session:
        tasks = [scrape_url_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and empty results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error scraping {urls[i]}: {result}")
            elif result:
                valid_results.append(result)
        
        return valid_results


def scrape_url(url):
    """Fallback synchronous version"""
    try:
        response = requests.get(url, timeout=5)  # Reduced timeout
        response.raise_for_status()

        extractor = extractors.ArticleExtractor()
        content = extractor.get_content(response.text)

        return content.strip()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return ""

