from serpapi import GoogleSearch
import os
from dotenv import load_dotenv

load_dotenv()


def search_serpapi(query, max_results=3):
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
