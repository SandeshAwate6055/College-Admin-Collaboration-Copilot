import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api import chat, datasets, intelligence, tickets, search, whatsapp, platform
from app.database.session import Base, engine

# Auto-create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VIT College Talent & Knowledge Platform")

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
app.include_router(platform.router, prefix="/api", tags=["Platform"])
app.include_router(whatsapp.router, tags=["WhatsApp"])

# Serve the UI (React production build with fallback to legacy UI)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

@app.get("/vit_header_logo.png")
def serve_header_logo():
    logo_file = os.path.join(DIST_DIR, "vit_header_logo.png")
    if os.path.exists(logo_file):
        return FileResponse(logo_file)
    return FileResponse(os.path.join(os.path.dirname(PROJECT_ROOT), "image.png"))

@app.get("/vit_logo.png")
def serve_logo():
    logo_file = os.path.join(DIST_DIR, "vit_logo.png")
    if os.path.exists(logo_file):
        return FileResponse(logo_file)
    return FileResponse(os.path.join(os.path.dirname(PROJECT_ROOT), "image copy.png"))

@app.get("/")
def root():
    react_index = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(react_index):
        return FileResponse(react_index)
    return FileResponse(os.path.join(PROJECT_ROOT, "ui.html"))

@app.get("/ui")
def serve_ui():
    react_index = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(react_index):
        return FileResponse(react_index)
    return FileResponse(os.path.join(PROJECT_ROOT, "ui.html"))

@app.get("/legacy-ui")
def serve_legacy_ui():
    return FileResponse(os.path.join(PROJECT_ROOT, "ui.html"))
