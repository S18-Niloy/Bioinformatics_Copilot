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

> 🔒 **Security**: See [SECURITY.md](SECURITY.md) for comprehensive security guidelines and best practices.

---

## 🔐 Security Overview

This project implements enterprise-grade security:
- **JWT Authentication**: 15-minute access tokens + 7-day refresh tokens
- **Password Security**: Argon2 hashing with minimum complexity requirements
- **Input Validation**: Pydantic models enforce strict type and length validation
- **CORS Protection**: Whitelist-based origin validation
- **Error Handling**: Stack traces not exposed in production
- **Database**: SQLAlchemy ORM prevents SQL injection
- **Secrets Management**: All sensitive config via environment variables

For detailed security information, see [SECURITY.md](SECURITY.md).

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

### 0. Environment Setup

Before running locally, configure your environment:

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (for development, defaults are fine)
# For production, see SECURITY.md for requirements
```

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

### Setup

```bash
# Copy local environment override
cp docker-compose.override.yml.example docker-compose.override.yml

# (Optional) Edit docker-compose.override.yml for custom settings
```

### Run

```bash
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend  → http://localhost:8000

### Production Deployment

For production, set environment variables before deploying:

```bash
docker run \
  --env ENVIRONMENT=production \
  --env JWT_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))') \
  --env DATABASE_URL=postgresql://user:password@host/dbname \
  --env ALLOWED_ORIGINS=https://yourdomain.com \
  --env ALLOWED_HOSTS=api.yourdomain.com \
  -p 8000:8000 \
  bioinformatics-copilot-backend:latest
```

See [SECURITY.md](SECURITY.md) for complete production deployment guidelines.

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
