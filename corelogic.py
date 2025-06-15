from scraper import scrape_url
from summarizer import chunk_text, get_embedding
from faiss_store import FAISSStore
import openai
from dotenv import load_dotenv
import os
from embedding_cache import load_cache, save_cache, get_or_embed
from serp_api import search_serpapi

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def prepare_knowledge_base(urls):
    cache = load_cache()
    all_chunks = []
    all_embeddings = []

    for url in urls:
        print(f"Scraping: {url}")
        text = scrape_url(url)
        if not text:
            continue
        chunks = chunk_text(text)
        for chunk in chunks:
            embedding = get_or_embed(chunk, get_embedding, cache)
            all_chunks.append(chunk)
            all_embeddings.append(embedding)
    save_cache(cache)

    if all_embeddings:
        dim = len(all_embeddings[0])
    else:
        dim = 0
    store = FAISSStore(dim)
    store.add(all_embeddings, all_chunks)
    return store


def ask_llm(question, context_chunks):
    context = "\n\n---\n\n".join(context_chunks)
    prompt = f"""Answer the question below using the following context and keep your answer concise and to the point should be in 100 words:\n\n{context}\n\nQuestion: {question}\nAnswer:"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def get_answer(question):
    try:
        urls = search_serpapi(question)
        print(f"Found {len(urls)} relevant URLs")
        store = prepare_knowledge_base(urls)

        question_embedding = get_embedding(question)
        top_chunks = store.search(question_embedding, top_k=3)
        print(f"Found {len(top_chunks)} relevant chunks")
        answer = ask_llm(question, top_chunks)
        print("\n🧠 Answer:\n", answer)
        return answer, urls
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request.", []