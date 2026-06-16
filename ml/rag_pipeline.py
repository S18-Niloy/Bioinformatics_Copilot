"""
Local RAG pipeline:
  - Embeddings: sentence-transformers/all-MiniLM-L6-v2 (~80 MB, CPU)
  - Vector store: FAISS (in-memory + pickled to disk)
  - Generator: google/flan-t5-small (~300 MB, CPU)
Everything runs offline after first model download. No paid API.
"""
import os, pickle
from pathlib import Path
from typing import List, Dict

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline

ROOT = Path(__file__).parent
KB_PATH = ROOT / "data" / "knowledge.txt"
INDEX_PATH = ROOT / "faiss.index"
CHUNKS_PATH = ROOT / "chunks.pkl"

_embed_model = None
_gen_pipe = None
_index = None
_chunks: List[str] = []

def _get_embed():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embed_model

def _get_generator():
    global _gen_pipe
    if _gen_pipe is None:
        _gen_pipe = pipeline("text2text-generation", model="google/flan-t5-small")
    return _gen_pipe

def _chunk(text: str, max_words: int = 80) -> List[str]:
    out = []
    for para in text.split("\n"):
        para = para.strip()
        if not para: continue
        words = para.split()
        for i in range(0, len(words), max_words):
            out.append(" ".join(words[i:i+max_words]))
    return out

def build_index():
    global _index, _chunks
    text = KB_PATH.read_text(encoding="utf-8")
    _chunks = _chunk(text)
    embs = _get_embed().encode(_chunks, convert_to_numpy=True, normalize_embeddings=True)
    _index = faiss.IndexFlatIP(embs.shape[1])
    _index.add(embs.astype("float32"))
    faiss.write_index(_index, str(INDEX_PATH))
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(_chunks, f)
    return {"chunks": len(_chunks)}

def _load():
    global _index, _chunks
    if _index is not None and _chunks: return
    if not INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        build_index()
    else:
        _index = faiss.read_index(str(INDEX_PATH))
        with open(CHUNKS_PATH, "rb") as f:
            _chunks = pickle.load(f)

def retrieve(query: str, k: int = 4) -> List[Dict]:
    _load()
    q = _get_embed().encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    scores, idxs = _index.search(q, k)
    return [{"text": _chunks[i], "score": float(s)} for i, s in zip(idxs[0], scores[0]) if i >= 0]

def answer(question: str) -> Dict:
    ctx = retrieve(question, k=4)
    context_text = "\n".join(f"- {c['text']}" for c in ctx)
    prompt = (
        "You are a bioinformatics research assistant. Use the context to answer the question. "
        "If the context does not contain the answer, say you don't know.\n\n"
        f"Context:\n{context_text}\n\nQuestion: {question}\nAnswer:"
    )
    gen = _get_generator()
    out = gen(prompt, max_new_tokens=180, do_sample=False)[0]["generated_text"]
    return {"answer": out.strip(), "sources": ctx}

if __name__ == "__main__":
    print(build_index())
    print(answer("What is GC content and why does it matter?"))
