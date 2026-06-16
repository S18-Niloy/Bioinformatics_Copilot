# Bioinformatics Copilot (Ongoing)

Full-stack SaaS combining:
- RAG-based AI assistant (FAISS + sentence-transformers, fully local, no paid APIs)
- Gene / protein sequence analysis (GC content, ORFs, translation, pairwise alignment)
- Protein similarity search via embeddings
- Graph Neural Network module (PyTorch Geometric, GCN on a toy protein-protein interaction graph)
- Interactive protein graph generator on `/gnn` with selectable node count and custom protein names
- Research-style explanation generator using a local HuggingFace LLM (flan-t5-small by default — runs on CPU)
- Next.js frontend, FastAPI backend, JWT auth, SQLite (Postgres-ready), Docker

> All models default to **free, local, CPU-friendly** weights from HuggingFace.
> No OpenAI / paid API keys required.

---

## 🗂 Project Tree

```
bioinformatics-copilot/
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── sequence.py
│   │   ├── protein.py
│   │   ├── gnn.py
│   │   └── users.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── sequence_service.py
│   ├── data/
│   │   └── proteins.fasta
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── pages/
│   │   ├── _app.js
│   │   ├── index.js
│   │   ├── login.js
│   │   ├── chat.js
│   │   ├── sequence.js
│   │   └── gnn.js
│   ├── components/
│   │   ├── Layout.js
│   │   └── Nav.js
│   └── styles/
│       └── globals.css
├── ml/
│   ├── rag_pipeline.py
│   ├── gnn_model.py
│   ├── embeddings.py
│   ├── train_gnn.py
│   ├── data/
│   │   └── knowledge.txt
│   └── requirements.txt
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

---

## 🚀 Running Locally (no Docker)

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Build the RAG index (one-off, downloads ~80MB embedding model)
python -c "from ml.rag_pipeline import build_index; build_index()"
# Pre-train tiny GNN (writes ml/gnn_checkpoint.pt)
python ../ml/train_gnn.py
# Start API
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:3000

### 3. GNN Graph Generator
Open `http://localhost:3000/gnn` and enter:
- `Number of nodes` to control graph size
- `Protein names` as comma-separated values to seed the graph

The page generates an interactive protein graph and returns node/edge data from the backend.

### 4. Default user

Register on `/login` or POST `/api/users/register` with `{username, password}`.

---

## 🐳 Running with Docker

```bash
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend  → http://localhost:8000

---

## 🔌 Key API Endpoints

| Method | Path                       | Purpose                                   |
| ------ | -------------------------- | ----------------------------------------- |
| POST   | /api/users/register        | Create user                               |
| POST   | /api/users/login           | Get JWT                                   |
| POST   | /api/chat                  | RAG-powered bio Q&A                       |
| POST   | /api/sequence/analyze      | GC%, length, ORFs, translation            |
| POST   | /api/sequence/align        | Pairwise alignment                        |
| POST   | /api/protein/similar       | Embedding similarity search               |
| POST   | /api/gnn/predict           | GCN node-class prediction on toy PPI graph|
| POST   | /api/gnn/graph             | Generate a custom protein graph by node count and protein names |

All ML endpoints (except /users/*) require `Authorization: Bearer <jwt>`.

---

## 📦 Producing the ZIP

```bash
zip -r bioinformatics-copilot.zip bioinformatics-copilot
```
