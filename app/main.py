import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api import chat, datasets, intelligence, tickets, search, whatsapp
from app.database.session import Base, engine

# Auto-create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="College Admin Copilot")

# Allow CORS so the UI can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(tickets.router)
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(datasets.router, prefix="/api", tags=["Datasets"])
app.include_router(intelligence.router, prefix="/api", tags=["Intelligence"])
app.include_router(whatsapp.router, tags=["WhatsApp"])

# Serve the UI
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.get("/")
def root():
    return FileResponse(os.path.join(PROJECT_ROOT, "ui.html"))

@app.get("/ui")
def serve_ui():
    return FileResponse(os.path.join(PROJECT_ROOT, "ui.html"))
