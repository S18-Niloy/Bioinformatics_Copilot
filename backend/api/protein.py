from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import get_current_user
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from ml.embeddings import similar_proteins

router = APIRouter(prefix="/api/protein", tags=["protein"])

class SimilarIn(BaseModel):
    sequence: str
    top_k: int = 5

@router.post("/similar")
def similar(body: SimilarIn, user=Depends(get_current_user)):
    return {"results": similar_proteins(body.sequence, body.top_k)}
