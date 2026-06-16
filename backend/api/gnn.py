from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from auth import get_current_user
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from ml.gnn_model import predict

router = APIRouter(prefix="/api/gnn", tags=["gnn"])

class GnnIn(BaseModel):
    node_index: Optional[int] = None  # if None, returns predictions for all nodes

@router.post("/predict")
def gnn_predict(body: GnnIn, user=Depends(get_current_user)):
    return predict(body.node_index)
