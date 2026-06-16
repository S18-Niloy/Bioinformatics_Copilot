from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models.user import User  # noqa: register
from api import users, chat, sequence, protein, gnn

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bioinformatics Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(chat.router)
app.include_router(sequence.router)
app.include_router(protein.router)
app.include_router(gnn.router)

@app.get("/")
def root():
    return {"name": "Bioinformatics Copilot", "docs": "/docs"}
