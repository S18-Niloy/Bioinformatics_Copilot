from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from auth import get_current_user
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from ml.gnn_model import predict, generate_graph

router = APIRouter(prefix="/api/gnn", tags=["gnn"])

class GnnIn(BaseModel):
    node_index: Optional[int] = None  # if None, returns predictions for all nodes

class GnnGraphIn(BaseModel):
    node_count: Optional[int] = None
    protein_names: Optional[List[str]] = None

@router.post("/predict")
def gnn_predict(body: GnnIn, user=Depends(get_current_user)):
    return predict(body.node_index)

@router.post("/graph")
def gnn_graph(body: GnnGraphIn, user=Depends(get_current_user)):
    return generate_graph(node_count=body.node_count, protein_names=body.protein_names)
