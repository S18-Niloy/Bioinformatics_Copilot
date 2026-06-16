from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import get_current_user
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from ml.rag_pipeline import answer

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatIn(BaseModel):
    question: str

@router.post("")
def chat(body: ChatIn, user=Depends(get_current_user)):
    return answer(body.question)
