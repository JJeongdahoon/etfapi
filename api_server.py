# api_server.py
from fastapi import FastAPI
from pydantic import BaseModel
from core_logic import handle_query

# FastAPI 앱 생성
app = FastAPI(title="ETF 탐색 API")

# 단순 세션 메시지 저장 (실서비스면 세션ID별로 분리 추천)
messages = [
    {"role": "assistant", "content": "앙앙 어떤 ETF를 보여줄까?."}
]

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_agent(req: QueryRequest):
    # main.py 로직 호출
    answer = handle_query(req.query, messages)
    return {
        "query": req.query,
        "answer": answer
    }
