from scraper import scrape_url
from summarizer import chunk_text, get_embedding
from faiss_store import FAISSStore
import openai
from dotenv import load_dotenv
import os
from embedding_cache import load_cache, save_cache, get_or_embed
INDEX_PATH = "kb.index"

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def prepare_knowledge_base(urls):
    if os.path.exists(INDEX_PATH):
        print("📦 Loading existing FAISS index from disk...")
        dummy_dim = 1536  # adjust if using different embedding model
        store = FAISSStore(dummy_dim)
        store.load(INDEX_PATH)
        return store

    # Else build new index
    all_chunks = []
    all_embeddings = []
    cache = load_cache()

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

    dim = len(all_embeddings[0]) if all_embeddings else 0
    store = FAISSStore(dim)
    store.add(all_embeddings, all_chunks)
    store.save(INDEX_PATH)
    print("💾 Saved FAISS index to disk.")

    return store


def ask_llm(question, context_chunks):
    context = "\n\n---\n\n".join(context_chunks)
    prompt = f"""Answer the question below using the following context:\n\n{context}\n\nQuestion: {question}\nAnswer:"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def main():
    urls = []
    print("Enter URLs (one per line). Type 'done' when finished:")
    while True:
        url = input("URL: ").strip()
        if url.lower() == "done":
            break
        urls.append(url)

    if not urls:
        print("No URLs provided.")
        return

    print("\nPreparing knowledge base...")
    store = prepare_knowledge_base(urls)

    while True:
        question = input("\nAsk a question (or type 'exit' to quit): ").strip()
        if question.lower() == "exit":
            break

        question_embedding = get_embedding(question)
        top_chunks = store.search(question_embedding, top_k=3)
        print(f"Found {len(top_chunks)} relevant chunks")
        answer = ask_llm(question, top_chunks)
        print("\n🧠 Answer:\n", answer)


if __name__ == "__main__":
    main()
