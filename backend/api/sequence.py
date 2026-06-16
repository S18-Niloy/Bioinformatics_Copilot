from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import get_current_user
from services.sequence_service import analyze_sequence, align_sequences

router = APIRouter(prefix="/api/sequence", tags=["sequence"])

class AnalyzeIn(BaseModel):
    sequence: str

class AlignIn(BaseModel):
    seq_a: str
    seq_b: str

@router.post("/analyze")
def analyze(body: AnalyzeIn, user=Depends(get_current_user)):
    try:
        return analyze_sequence(body.sequence)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/align")
def align(body: AlignIn, user=Depends(get_current_user)):
    return align_sequences(body.seq_a, body.seq_b)
