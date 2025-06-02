# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import List, Dict, Optional
import re
import logging

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

model = ChatOpenAI(
    model="deepseek/deepseek-r1-0528-qwen3-8b:free",
    api_key="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",
    base_url="https://openrouter.ai/api/v1",
)

prompt_template = PromptTemplate.from_template("""
You are an expert AI tutor that explains competitive exam problems step-by-step.

Given a question in LaTeX and its final answer:
1. Convert it to a readable format.
2. Solve the following question step-by-step in a fully structured and logical manner. Use the format: Step 1:, Step 2:, Step 3:, ..., and so on. Do not use any markdown symbols like *, **, #, or _.
3. Avoid all formatting styles. Output should be in plain text only, clearly broken into steps.
4. Final answer should be same.
5. dont's use astericks in the response.


Question: {question}
Final Answer: {answer}

""")

class ChatRequest(BaseModel):
    session_id: str
    question: str
    answer: str

class ChatResponse(BaseModel):
    reply: str
    difficulty: Optional[str] = None
    history: List[Dict[str, str]]

chat_histories: Dict[str, List[Dict[str, str]]] = {}
MAX_HISTORY_LENGTH = 10

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        question = clean_latex(request.question)
        answer = request.answer
        session_id = request.session_id

        prompt = prompt_template.format(question=question, answer=answer)
        user_message = f"Q: {question}\nA: {answer}"

        result = model.invoke(prompt)
        ai_reply = result.content.strip()

        difficulty_match = re.search(r"Difficulty Level\s*:\s*(Easy|Medium|Hard)", ai_reply, re.IGNORECASE)
        difficulty = difficulty_match.group(1).capitalize() if difficulty_match else None

        if session_id not in chat_histories:
            chat_histories[session_id] = []

        chat_histories[session_id].append({
            "user": user_message,
            "ai": ai_reply
        })

        if len(chat_histories[session_id]) > MAX_HISTORY_LENGTH:
            chat_histories[session_id] = chat_histories[session_id][-MAX_HISTORY_LENGTH:]

        return ChatResponse(reply=ai_reply, difficulty=difficulty, history=chat_histories[session_id])

    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def clean_latex(text: str) -> str:
    text = re.sub(r'\\[a-zA-Z]+\*?', '', text)
    text = re.sub(r'[\{\}]', '', text)
    text = re.sub(r'\$', '', text)
    return text.strip()

