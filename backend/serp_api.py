from serpapi import GoogleSearch
import os
from dotenv import load_dotenv

load_dotenv()


def search_serpapi(query, max_results=5):
    """Get search results with snippets - much faster than scraping"""
    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_KEY"),
        "num": max_results
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    
    search_data = []
    for result in results.get("organic_results", []):
        search_data.append({
            "title": result.get("title", ""),
            "snippet": result.get("snippet", ""),
            "link": result.get("link", ""),
            "source": result.get("source", "")
        })
        if len(search_data) >= max_results:
            break

    return search_data


def search_serpapi_urls_only(query, max_results=3):
    """Legacy function for URL-only results"""
    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_KEY"),
        "num": max_results
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    links = []

    for result in results.get("organic_results", []):
        links.append(result["link"])
        if len(links) >= max_results:
            break

    return links
