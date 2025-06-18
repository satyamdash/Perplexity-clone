from .scraper import scrape_url
from .summarizer import chunk_text, get_embedding
from .faiss_store import FAISSStore
import openai
from dotenv import load_dotenv
import os
from .embedding_cache import load_cache, save_cache, get_or_embed
from .serp_api import search_serpapi

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


async def ask_llm(question, context_chunks):
    context = "\n\n---\n\n".join(context_chunks)
    prompt = f"""Answer the question below using the following context and keep your answer concise and to the point should be in 100 words:\n\n{context}\n\nQuestion: {question}\nAnswer:
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        stream=True
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


async def generate_follow_up_questions(question, answer):
    prompt = f"""Based on the following question and answer, generate 3 relevant follow-up questions that users might want to ask next. 
    Make them specific and related to the topic. Return only the questions, one per line, without numbering.

    Question: {question}
    Answer: {answer}

    Follow-up questions:"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )
    
    questions = response.choices[0].message.content.strip().split('\n')
    # Clean up the questions and filter out empty lines
    questions = [q.strip().replace('- ', '').replace('• ', '').replace('1. ', '').replace('2. ', '').replace('3. ', '') for q in questions if q.strip()]
    return questions[:3]  # Return max 3 questions


async def get_answer(question):
    try:
        urls = search_serpapi(question)
        print(f"Found {len(urls)} relevant URLs")
        store = prepare_knowledge_base(urls)

        question_embedding = get_embedding(question)
        top_chunks = store.search(question_embedding, top_k=3)
        print(f"Found {len(top_chunks)} relevant chunks")
        
        answer_stream = ask_llm(question, top_chunks)
        
        # Collect the full answer for follow-up questions
        full_answer = ""
        async def collect_answer():
            nonlocal full_answer
            async for chunk in answer_stream:
                full_answer += chunk
                yield chunk
        
        # Generate follow-up questions
        follow_up_questions = await generate_follow_up_questions(question, full_answer)
        
        return collect_answer(), urls, follow_up_questions
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request.", [], []