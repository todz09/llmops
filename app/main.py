import logging 
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel

from app.config import settings
from app.llm_client import ask_llm
from app.prompts import DEFAULT_VERSION

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="LLM Ops", version="0.1.0")


class AskRequest(BaseModel):
    question: str
    prompt_version: str = DEFAULT_VERSION
    
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: AskRequest):
    try:
        result = ask_llm(req.question, req.prompt_version)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail="LLM provider error")
    
    
@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)