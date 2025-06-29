from .scraper import scrape_urls_parallel
from .summarizer import chunk_text, get_embedding
from .faiss_store import FAISSStore
import openai
from dotenv import load_dotenv
import os
import asyncio
import hashlib
import json
import aiohttp
from .embedding_cache import load_cache, save_cache, get_or_embed
from .serp_api import search_serpapi, search_serpapi_urls_only

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Simple in-memory cache for search results (use Redis in production)
search_cache = {}
knowledge_base_cache = {}

def get_cache_key(query):
    """Generate cache key for query"""
    return hashlib.md5(query.encode()).hexdigest()


async def get_answer_ultra_fast(question):
    """Ultra-fast approach using LLM knowledge + web context (1-2s response)"""
    try:
        cache_key = get_cache_key(question + "_ultra")
        
        # Check cache first
        if cache_key in search_cache:
            print("Using cached ultra-fast result")
            cached_result = search_cache[cache_key]
            return cached_result['stream'], cached_result['urls'], cached_result['followups']

        # Use GPT-4o with enhanced prompting for current information
        prompt = f"""Answer the following question comprehensively using your knowledge. If the question requires very recent information (within the last few months), acknowledge what you might not know due to your knowledge cutoff and suggest what type of current sources would be helpful.

Question: {question}

Provide a detailed, helpful answer. If you mention specific facts, dates, or statistics, indicate your confidence level or knowledge cutoff limitations where relevant."""

        # Start follow-up generation in parallel
        followup_task = asyncio.create_task(generate_follow_up_questions(question))
        
        # Stream the answer
        answer_stream = ask_llm_ultra_fast(prompt)
        
        # Wait for follow-up questions
        follow_up_questions = await followup_task
        
        # No sources for ultra-fast mode (uses LLM knowledge directly)
        urls = []
        
        # Cache the result structure (not the stream itself)
        search_cache[cache_key] = {
            'urls': urls,
            'followups': follow_up_questions,
            'stream': None  # Can't cache streams
        }
        
        return answer_stream, urls, follow_up_questions
    except Exception as e:
        print(f"Error in ultra-fast answer: {e}")
        error_stream = create_error_stream("An error occurred while processing your request.")
        return error_stream, [], []


async def ask_llm_ultra_fast(prompt):
    """Ultra-fast LLM call with optimized settings"""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # Fastest model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        stream=True,
        max_tokens=400
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content




async def get_answer_fast(question):
    """Ultra-fast approach using search snippets only"""
    try:
        cache_key = get_cache_key(question)
        
        # Check search cache first
        if cache_key in search_cache:
            print("Using cached search results")
            search_results = search_cache[cache_key]
        else:
            search_results = search_serpapi(question)
            search_cache[cache_key] = search_results
            print(f"Found {len(search_results)} search results")

        if not search_results:
            error_stream = create_error_stream("No search results found.")
            return error_stream, [], []

        # Prepare context from snippets (no scraping needed!)
        context_parts = []
        urls = []
        for result in search_results:
            if result['snippet']:
                context_parts.append(f"Source: {result['title']}\n{result['snippet']}")
                urls.append(result['link'])

        if not context_parts:
            error_stream = create_error_stream("No relevant content found in search results.")
            return error_stream, urls, []

        # Start follow-up generation in parallel
        followup_task = asyncio.create_task(generate_follow_up_questions(question))
        
        # Stream the answer using snippets as context
        answer_stream = ask_llm_with_snippets(question, context_parts)
        
        # Wait for follow-up questions
        follow_up_questions = await followup_task
        
        return answer_stream, urls, follow_up_questions
    except Exception as e:
        print(f"Error in fast answer: {e}")
        error_stream = create_error_stream("An error occurred while processing your request.")
        return error_stream, [], []


async def ask_llm_with_snippets(question, context_parts):
    """Stream answer using search snippets as context"""
    context = "\n\n---\n\n".join(context_parts)
    prompt = f"""Answer the question below using the following search results. Provide a comprehensive answer based on the available information:

{context}

Question: {question}

Answer (be informative and cite sources when relevant):"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # Fast model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        stream=True,
        max_tokens=300
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


async def get_answer_deep(question):
    """Deep dive approach using web scraping for comprehensive answers"""
    try:
        cache_key = get_cache_key(question + "_deep")
        
        # Check search cache first
        if cache_key in search_cache:
            print("Using cached deep search results")
            urls = search_cache[cache_key]
        else:
            urls = search_serpapi_urls_only(question, max_results=3)  # Limit to 3 for deep dive
            search_cache[cache_key] = urls
            print(f"Found {len(urls)} URLs for deep scraping")

        # Parallel knowledge base preparation with scraping
        store = await prepare_knowledge_base_parallel(urls)
        if not store:
            error_stream = create_error_stream("No relevant content found after scraping.")
            return error_stream, urls, []

        # Get relevant chunks
        question_embedding = get_embedding(question)
        top_chunks = store.search(question_embedding, top_k=8)  # More chunks for deep analysis
        print(f"Found {len(top_chunks)} relevant chunks from scraped content")
        
        # Start follow-up generation in parallel
        followup_task = asyncio.create_task(generate_follow_up_questions(question))
        
        # Stream the comprehensive answer
        answer_stream = ask_llm_deep(question, top_chunks)
        
        # Wait for follow-up questions
        follow_up_questions = await followup_task
        
        return answer_stream, urls, follow_up_questions
    except Exception as e:
        print(f"Error in deep answer: {e}")
        error_stream = create_error_stream("An error occurred while processing your deep dive request.")
        return error_stream, [], []


async def ask_llm_deep(question, context_chunks):
    """Deep analysis with more comprehensive prompting"""
    context = "\n\n---\n\n".join(context_chunks)
    prompt = f"""Provide a comprehensive and detailed answer to the question below using the following scraped web content. 
    
Include:
- A thorough analysis of the topic
- Multiple perspectives if available
- Specific details and examples from the sources
- Key insights and implications

Context from web sources:
{context}

Question: {question}

Comprehensive Answer:"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        stream=True,
        max_tokens=500  # More tokens for comprehensive answers
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


async def prepare_knowledge_base_parallel(urls):
    """Optimized parallel knowledge base preparation"""
    cache_key = "_".join(sorted(urls))
    
    # Check if we have cached knowledge base
    if cache_key in knowledge_base_cache:
        print("Using cached knowledge base")
        return knowledge_base_cache[cache_key]
    
    cache = load_cache()
    all_chunks = []
    all_embeddings = []

    # Parallel scraping - this is the key optimization!
    print(f"Scraping {len(urls)} URLs in parallel...")
    scraped_texts = await scrape_urls_parallel(urls)
    
    # Process all scraped content
    for text in scraped_texts:
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
        store = FAISSStore(dim)
        store.add(all_embeddings, all_chunks)
        
        # Cache the knowledge base
        knowledge_base_cache[cache_key] = store
        print(f"Created knowledge base with {len(all_chunks)} chunks")
        return store
    else:
        return None


async def ask_llm(question, context_chunks):
    """Simplified streaming LLM call"""
    context = "\n\n---\n\n".join(context_chunks)
    prompt = f"""Answer the question below using the following context and keep your answer concise and to the point should be in 100 words:\n\n{context}\n\nQuestion: {question}\nAnswer:
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # Faster model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        stream=True
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


async def generate_follow_up_questions(question, answer=None):
    """Generate follow-up questions (can run in parallel)"""
    prompt = f"""Based on the following question, generate 3 relevant follow-up questions that users might want to ask next. 
    Make them specific and related to the topic. Return only the questions, one per line, without numbering.

    Question: {question}

    Follow-up questions:"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Faster model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        
        questions = response.choices[0].message.content.strip().split('\n')
        questions = [q.strip().replace('- ', '').replace('• ', '').replace('1. ', '').replace('2. ', '').replace('3. ', '') 
                    for q in questions if q.strip()]
        return questions[:3]
    except Exception as e:
        print(f"Error generating follow-up questions: {e}")
        return []


async def create_error_stream(error_message):
    """Create an async generator for error messages"""
    yield error_message

async def get_answer(question):
    """Optimized main function with caching and parallel processing"""
    try:
        cache_key = get_cache_key(question)
        
        # Check search cache first
        if cache_key in search_cache:
            print("Using cached search results")
            urls = search_cache[cache_key]
        else:
            urls = search_serpapi_urls_only(question)
            search_cache[cache_key] = urls
            print(f"Found {len(urls)} relevant URLs")

        # Parallel knowledge base preparation
        store = await prepare_knowledge_base_parallel(urls)
        if not store:
            error_stream = create_error_stream("No relevant content found.")
            return error_stream, urls, []

        # Get relevant chunks
        question_embedding = get_embedding(question)
        top_chunks = store.search(question_embedding, top_k=5)  # Increased for better context
        print(f"Found {len(top_chunks)} relevant chunks")
        
        # Start follow-up generation in parallel (fire and forget)
        followup_task = asyncio.create_task(generate_follow_up_questions(question))
        
        # Stream the answer
        answer_stream = ask_llm(question, top_chunks)
        
        # Wait for follow-up questions
        follow_up_questions = await followup_task
        
        return answer_stream, urls, follow_up_questions
    except Exception as e:
        print(f"Error: {e}")
        error_stream = create_error_stream("An error occurred while processing your request.")
        return error_stream, [], []