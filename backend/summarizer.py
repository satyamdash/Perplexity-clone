import openai
import os
from dotenv import load_dotenv
import tiktoken

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

def chunk_text(text, max_tokens=500):
    encoding = tiktoken.get_encoding("cl100k_base")
    words = text.split()
    chunk,chunks = [],[]

    for word in words:
        chunk.append(word)
        if len(encoding.encode(" ".join(chunk))) > max_tokens:
            chunks.append(" ".join(chunk))
            chunk = []
    
    if chunk:
        chunks.append(" ".join(chunk))
    print(f"Chunked {len(words)} words into {len(chunks)} chunks")
    return chunks
            
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ").strip()
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

