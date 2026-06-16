"""
Enhanced Tiny GCN for Protein-Protein Interaction Visualization
Adds:
- Graph visualization
- Prediction coloring
- GCN embeddings visualization
- TSNE latent space
"""

from pathlib import Path
from typing import Optional, Dict, List
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

import networkx as nx
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

# -----------------------------
# CONFIG
# -----------------------------
ROOT = Path(__file__).parent
CKPT = ROOT / "gnn_checkpoint.pt"

NODE_NAMES = ["HBA","HBB","ALB","COL1A1","EGFR","BRCA1","KRAS","TP53","INS","GAPDH"]

LABELS = [0,0,0,0,1,1,1,1,0,1]
KNOWN_LABELS = {name: label for name, label in zip(NODE_NAMES, LABELS)}

torch.manual_seed(0)
FEATURES = torch.randn(len(NODE_NAMES), 8)

EDGES = [
    (0,1),(1,0),(0,2),(2,0),(3,2),(2,3),
    (4,5),(5,4),(4,6),(6,4),
    (5,7),(7,5),(6,7),(7,6),
    (8,2),(2,8),(9,4),(4,9),(9,6),(6,9),
]

edge_index = torch.tensor(EDGES, dtype=torch.long).t().contiguous()

DATA = Data(
    x=FEATURES,
    edge_index=edge_index,
    y=torch.tensor(LABELS)
)


def build_graph_edges(node_count: int):
    edges = []
    for i in range(node_count - 1):
        edges.append((i, i + 1))
    for i in range(node_count - 2):
        edges.append((i, i + 2))
    if node_count > 4:
        for i in range(node_count - 3):
            edges.append((i, i + 3))
    return edges


def generate_graph(node_count: Optional[int] = None, protein_names: Optional[List[str]] = None):
    names = [name.strip() for name in (protein_names or []) if name.strip()]
    if node_count is None:
        node_count = max(len(names), 3)
    node_count = max(1, node_count)

    if names:
        names = names[:node_count]

    while len(names) < node_count:
        for candidate in NODE_NAMES:
            if candidate not in names:
                names.append(candidate)
                break
        else:
            names.append(f"Protein_{len(names) + 1}")

    nodes = []
    for i, name in enumerate(names):
        label = KNOWN_LABELS.get(name, 1 if sum(ord(c) for c in name) % 2 else 0)
        prob = [0.8, 0.2] if label == 0 else [0.2, 0.8]
        nodes.append({
            "id": i,
            "name": name,
            "pred": int(label),
            "label": "enzyme" if label == 1 else "non-enzyme",
            "prob": prob,
        })

    edges = build_graph_edges(len(names))

    return {
        "node_count": len(names),
        "nodes": nodes,
        "edges": edges,
    }


# -----------------------------
# MODEL
# -----------------------------
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

def load_model():
    global _model
    if _model is not None:
        return _model

    model = GCN()

    if CKPT.exists():
        model.load_state_dict(torch.load(CKPT, map_location="cpu"))

    model.eval()
    _model = model
    return model

# -----------------------------
# PREDICTION
# -----------------------------
@torch.no_grad()
def predict(node_index: Optional[int] = None):
    model = load_model()
    logits = model(DATA.x, DATA.edge_index)
    probs = F.softmax(logits, dim=-1)
    preds = probs.argmax(dim=-1)

    results = []
    for i in range(len(NODE_NAMES)):
        results.append({
            "node": NODE_NAMES[i],
            "pred": int(preds[i]),
            "label": "enzyme" if preds[i]==1 else "non-enzyme",
            "prob": probs[i].tolist()
        })

    if node_index is None:
        return results

    return results[node_index] if 0 <= node_index < len(results) else None

# -----------------------------
# GRAPH VISUALIZATION
# -----------------------------
def visualize_graph(colored=False):
    G = nx.Graph()

    preds = predict()

    for i, name in enumerate(NODE_NAMES):
        G.add_node(i, label=name)

    for s, d in EDGES:
        G.add_edge(s, d)

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(8,6))

    if colored:
        colors = ["red" if p["pred"]==1 else "blue" for p in preds]
    else:
        colors = "lightgray"

    nx.draw(
        G,
        pos,
        with_labels=True,
        labels={i: NODE_NAMES[i] for i in range(len(NODE_NAMES))},
        node_color=colors,
        node_size=800,
        edge_color="gray"
    )

    plt.title("Protein-Protein Interaction Graph")
    plt.show()

# -----------------------------
# EMBEDDING VISUALIZATION (GCN SPACE)
# -----------------------------
def visualize_embeddings():
    model = load_model()

    with torch.no_grad():
        h = model.c1(DATA.x, DATA.edge_index)
        h = torch.relu(h)

    emb_2d = TSNE(n_components=2, random_state=42).fit_transform(h.numpy())

    plt.figure(figsize=(8,6))
    plt.scatter(emb_2d[:,0], emb_2d[:,1])

    for i, name in enumerate(NODE_NAMES):
        plt.text(emb_2d[i,0], emb_2d[i,1], name)

    plt.title("GCN Learned Embeddings (t-SNE)")
    plt.show()

# -----------------------------
# MESSAGE PASSING INSPECTION
# -----------------------------
def inspect_message_passing(node=0):
    model = load_model()

    with torch.no_grad():
        raw = DATA.x[node]
        hidden = model.c1(DATA.x, DATA.edge_index)[node]
        output = model(DATA.x, DATA.edge_index)[node]

    print("\n--- MESSAGE PASSING INSIGHT ---")
    print("Node:", NODE_NAMES[node])
    print("Raw features:", raw)
    print("After GCN layer:", hidden)
    print("Final logits:", output)

# -----------------------------
# SINGLE NODE QUERY
# -----------------------------
def predict_node(i: int):
    res = predict()
    return res[i] if 0 <= i < len(res) else None

# -----------------------------
# MAIN DEMO
# -----------------------------
if __name__ == "__main__":
    print("\nRunning predictions...")
    print(predict())

    print("\nVisualizing graph...")
    visualize_graph(colored=True)

    print("\nVisualizing embeddings...")
    visualize_embeddings()

    print("\nInspecting message passing...")
    inspect_message_passing(4)