"""
Tiny GCN node-classification model over a toy protein-protein interaction
graph (10 nodes, 2 classes: enzyme=1, non-enzyme=0). Trained briefly and
checkpointed by ml/train_gnn.py.
"""
from pathlib import Path
from typing import Optional, Dict
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

ROOT = Path(__file__).parent
CKPT = ROOT / "gnn_checkpoint.pt"

NODE_NAMES = ["HBA","HBB","ALB","COL1A1","EGFR","BRCA1","KRAS","TP53","INS","GAPDH"]
# 0 = non-enzyme/structural, 1 = enzyme/kinase/etc
LABELS    = [0,    0,    0,    0,        1,     1,      1,    1,      0,     1]
# 8-dim toy features per node (length, GC-like, hydrophobicity, etc. — illustrative)
torch.manual_seed(0)
FEATURES = torch.randn(len(NODE_NAMES), 8)

EDGES = [
    (0,1),(1,0),(0,2),(2,0),(3,2),(2,3),(4,5),(5,4),(4,6),(6,4),
    (5,7),(7,5),(6,7),(7,6),(8,2),(2,8),(9,4),(4,9),(9,6),(6,9),
]
edge_index = torch.tensor(EDGES, dtype=torch.long).t().contiguous()

DATA = Data(x=FEATURES, edge_index=edge_index, y=torch.tensor(LABELS))

class GCN(torch.nn.Module):
    def __init__(self, in_dim=8, hid=16, out_dim=2):
        super().__init__()
        self.c1 = GCNConv(in_dim, hid)
        self.c2 = GCNConv(hid, out_dim)
    def forward(self, x, edge_index):
        h = F.relu(self.c1(x, edge_index))
        h = F.dropout(h, p=0.3, training=self.training)
        return self.c2(h, edge_index)

_model: Optional[GCN] = None

def _load_model() -> GCN:
    global _model
    if _model is not None: return _model
    m = GCN()
    if CKPT.exists():
        m.load_state_dict(torch.load(CKPT, map_location="cpu"))
    m.eval()
    _model = m
    return m

@torch.no_grad()
def predict(node_index: Optional[int] = None) -> Dict:
    m = _load_model()
    logits = m(DATA.x, DATA.edge_index)
    probs = F.softmax(logits, dim=-1)
    preds = probs.argmax(dim=-1).tolist()
    items = [
        {"node": NODE_NAMES[i], "predicted_class": int(preds[i]),
         "label_name": "enzyme" if preds[i]==1 else "non-enzyme",
         "prob": [round(p, 3) for p in probs[i].tolist()]}
        for i in range(len(NODE_NAMES))
    ]
    if node_index is not None and 0 <= node_index < len(NODE_NAMES):
        return {"node": items[node_index]}
    return {"nodes": items}
