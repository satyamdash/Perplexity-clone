from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .corelogic import get_answer
import json

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
    answer_stream, urls, follow_up_questions = await get_answer(query.question)
    
    async def generate():
        try:
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
