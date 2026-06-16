"""
Protein similarity search using sentence-transformer embeddings over
amino-acid sequences. For production use, swap in facebook/esm2_t6_8M_UR50D.
We use MiniLM here to keep the demo dependency-free and CPU fast.
"""
from pathlib import Path
from typing import List, Dict
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).parent
FASTA = ROOT.parent / "backend" / "data" / "proteins.fasta"

_model = None
_index = None
_records: List[Dict] = []

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def _parse_fasta(path: Path) -> List[Dict]:
    recs, name, seq = [], None, []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if name: recs.append({"id": name, "sequence": "".join(seq)})
            name, seq = line[1:].strip(), []
        else:
            seq.append(line.strip())
    if name: recs.append({"id": name, "sequence": "".join(seq)})
    return recs

def _build():
    global _index, _records
    _records = _parse_fasta(FASTA)
    # truncate long sequences to first 512 aa for embedding speed
    inputs = [r["sequence"][:512] for r in _records]
    embs = _get_model().encode(inputs, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    _index = faiss.IndexFlatIP(embs.shape[1])
    _index.add(embs)

def similar_proteins(query_seq: str, top_k: int = 5) -> List[Dict]:
    if _index is None: _build()
    q = _get_model().encode([query_seq[:512]], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    scores, idxs = _index.search(q, min(top_k, len(_records)))
    out = []
    for i, s in zip(idxs[0], scores[0]):
        if i < 0: continue
        r = _records[i]
        out.append({"id": r["id"], "score": float(s), "preview": r["sequence"][:60] + "..."})
    return out
