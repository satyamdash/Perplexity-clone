import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)
    
def ask_llm(question, documents):
    context = "\n\n---\n\n".join(documents)
    prompt = f"""Answer the question below based on the following documents:

    {context}

    Question: {question}
    Answer:"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using a valid model name
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
