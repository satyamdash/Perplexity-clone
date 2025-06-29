from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .corelogic import get_answer_fast, get_answer_deep, get_answer_ultra_fast
from .models.user import User
from .pydanticschemas.user import UserResponse, UserCreate
from .routers import users
from .dbclient import Base, engine

import json
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this to your Next.js domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)

class Query(BaseModel):
    question: str

class DeepQuery(BaseModel):
    question: str
    mode: str = "deep"  # "fast" or "deep"

Base.metadata.create_all(bind=engine)

@app.post("/api/ask")
async def ask_question(query: Query):
    """Ultra-fast answer using direct LLM (1-2s)"""
    answer_stream, urls, follow_up_questions = await get_answer_ultra_fast(query.question)
    
    async def generate():
        try:
            # Send mode info
            yield f"data: {json.dumps({'type': 'mode', 'mode': 'ultra'})}\n\n"
            
            # First send the URLs
            yield f"data: {json.dumps({'type': 'urls', 'urls': urls})}\n\n"
            
            # Then stream the answer
            async for chunk in answer_stream:
                yield f"data: {json.dumps({'type': 'answer', 'content': chunk})}\n\n"
            
            # Finally send follow-up questions
            yield f"data: {json.dumps({'type': 'follow_up_questions', 'questions': follow_up_questions})}\n\n"
            yield f"data: [DONE]\n\n"
        except Exception as e:
            print(f"Error in streaming: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'An error occurred while streaming the response.'})}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@app.post("/api/ask-deep")
async def ask_question_deep(query: Query):
    """Deep answer using web scraping"""
    answer_stream, urls, follow_up_questions = await get_answer_deep(query.question)
    
    async def generate():
        try:
            # Send mode info
            yield f"data: {json.dumps({'type': 'mode', 'mode': 'deep'})}\n\n"
            
            # Send status update
            yield f"data: {json.dumps({'type': 'status', 'message': 'Scraping websites for detailed information...'})}\n\n"
            
            # First send the URLs
            yield f"data: {json.dumps({'type': 'urls', 'urls': urls})}\n\n"
            
            # Then stream the answer
            async for chunk in answer_stream:
                yield f"data: {json.dumps({'type': 'answer', 'content': chunk})}\n\n"
            
            # Finally send follow-up questions
            yield f"data: {json.dumps({'type': 'follow_up_questions', 'questions': follow_up_questions})}\n\n"
            yield f"data: [DONE]\n\n"
        except Exception as e:
            print(f"Error in streaming: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'An error occurred while streaming the response.'})}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@app.post("/api/ask-serp")
async def ask_question_serp(query: Query):
    """Answer using SERP API + snippets (3-5s)"""
    answer_stream, urls, follow_up_questions = await get_answer_fast(query.question)
    
    async def generate():
        try:
            # Send mode info
            yield f"data: {json.dumps({'type': 'mode', 'mode': 'serp'})}\n\n"
            
            # Send status update
            yield f"data: {json.dumps({'type': 'status', 'message': 'Searching the web for current information...'})}\n\n"
            
            # First send the URLs
            yield f"data: {json.dumps({'type': 'urls', 'urls': urls})}\n\n"
            
            # Then stream the answer
            async for chunk in answer_stream:
                yield f"data: {json.dumps({'type': 'answer', 'content': chunk})}\n\n"
            
            # Finally send follow-up questions
            yield f"data: {json.dumps({'type': 'follow_up_questions', 'questions': follow_up_questions})}\n\n"
            yield f"data: [DONE]\n\n"
        except Exception as e:
            print(f"Error in SERP streaming: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'An error occurred while streaming the response.'})}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
