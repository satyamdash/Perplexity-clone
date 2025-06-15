import json
import os

CACHE_FILE = "embedding_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def get_or_embed(text, get_embedding_fn, cache):
    key = text.strip().replace("\n", " ")[:1000]  # truncate key to avoid huge cache keys
    if key in cache:
        print(f"Cache hit")
        return cache[key]
    embedding = get_embedding_fn(text)
    cache[key] = embedding
    return embedding
