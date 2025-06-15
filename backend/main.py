from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .corelogic import get_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this to your Next.js domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

@app.post("/api/ask")
async def ask_question(query: Query):
    answer, urls = get_answer(query.question)
    return { "answer": answer, "sources": urls }
