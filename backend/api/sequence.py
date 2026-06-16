from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
import logging
from auth import get_current_user
from services.sequence_service import analyze_sequence, align_sequences

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sequence", tags=["sequence"])

class AnalyzeIn(BaseModel):
    sequence: str = Field(..., min_length=1, max_length=100000)  # 100k char limit
    
    @validator("sequence")
    def validate_sequence(cls, v):
        """Validate sequence contains only valid DNA/RNA/Protein characters."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Sequence cannot be empty")
        # Only allow DNA/RNA/Protein characters (A-Z with some standard codes)
        if not all(c.upper() in "ACGTUNRYSWKMBDHV" for c in v):
            raise ValueError("Invalid sequence characters")
        return v.upper()

class AlignIn(BaseModel):
    seq_a: str = Field(..., min_length=1, max_length=50000)
    seq_b: str = Field(..., min_length=1, max_length=50000)
    
    @validator("seq_a", "seq_b", pre=False)
    def validate_sequences(cls, v):
        """Validate sequences contain only valid characters."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Sequence cannot be empty")
        if not all(c.upper() in "ACGTUNRYSWKMBDHV" for c in v):
            raise ValueError("Invalid sequence characters")
        return v.upper()

@router.post("/analyze")
def analyze(body: AnalyzeIn, user=Depends(get_current_user)):
    """Analyze sequence for GC content, length, ORFs, and translation."""
    try:
        result = analyze_sequence(body.sequence)
        logger.info(f"Sequence analyzed for user: {user.username}")
        return result
    except ValueError as e:
        logger.warning(f"Sequence validation error: {str(e)}")
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Sequence analysis error: {type(e).__name__}")
        raise HTTPException(500, "Analysis failed")

@router.post("/align")
def align(body: AlignIn, user=Depends(get_current_user)):
    """Perform pairwise alignment between two sequences."""
    try:
        result = align_sequences(body.seq_a, body.seq_b)
        logger.info(f"Sequences aligned for user: {user.username}")
        return result
    except Exception as e:
        logger.error(f"Alignment error: {type(e).__name__}")
        raise HTTPException(500, "Alignment failed")
