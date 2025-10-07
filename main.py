import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import text

# Configure templates
templates = Jinja2Templates(directory="templates")

# Load environment variables (load_dotenv() returns True/False but we ignore)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")  # Explicit path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Path Configuration ---
PROJECT_ROOT = Path(__file__).parent.resolve()  # Resolve absolute path
sys.path.insert(0, str(PROJECT_ROOT))  # Add project root to Python path

# --- Database Initialization (Risky) ---
db_engine = None  # Move outside try block to avoid shadowing
try:
    from app.database import init_db, engine, get_db
    from app.models.base import Base

    # Create tables if not exists
    Base.metadata.create_all(bind=engine)
    db_engine = engine
    logger.info("✅ Database initialized successfully")
    db_url = os.getenv('DATABASE_URL', '')
    if '@' in db_url:
        logger.info(f"📊 Connected to: {db_url.split('@')[1]}")
    else:
        logger.info(f"📊 Connected to: {db_url}")
except ImportError as e:
    logger.error(f"❌ Failed to import database module: {e}")
    raise SystemExit("Database initialization critical failure") from e  # Exit if critical
except Exception as e:
    logger.error(f"❌ Database connectivity failed: {e}")
    raise SystemExit("Database not available") from e

# --- FastAPI App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage model lifecycle with startup and shutdown events."""
    logger.info("🚀 Application starting up...")
    
    # --- Model Loading ---
    try:
        from app.ml.predictor import ObesityPredictor
        app.state.model = ObesityPredictor()
        if app.state.model and app.state.model.model:
            logger.info("✅ ML model loaded successfully")
        else:
            logger.warning("⚠️ ML model file missing or failed to load, using fallback...")
    except ImportError as e:
        logger.warning(f"⚠️ ML model module not found: {e}")
        app.state.model = None
    except Exception as e:
        logger.error(f"❌ ML model initialization failed: {e}")
        app.state.model = None

    # Temporary debug: Print all registered routes to diagnose 404.
    logger.info("\n--- Registered FastAPI Routes ---")
    for route in app.routes:
        if hasattr(route, "path"):
            logger.info(f"Path: {route.path}, Name: {route.name}, Methods: {getattr(route, 'methods', ['N/A'])}")
    logger.info("--------------------------------\n")

    yield  # Application runs here

    # --- Shutdown Logic ---
    logger.info("👋 Shutting down...")
    if db_engine:
        db_engine.dispose()
        logger.info("Database connections closed")

app = FastAPI(
    title=os.getenv("APP_NAME", "ObesiTrack"),
    description="Obesity Tracking & Prediction System",
    version=os.getenv("APP_VERSION", "1.0.0"),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# --- Static Files Setup ---
STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


logger.info(f"✅ Static files mounted from {STATIC_DIR}")

from app.routers import auth, prediction, metrics, pages

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["Predictions"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Dashboard"])
app.include_router(pages.router, tags=["Pages"])

# --- CORS Configuration ---
APP_ORIGINS = [
    "http://localhost:3000",  # React default
    "http://localhost:5173",  # Vite default
    "http://localhost:8080",  # Common alternate
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response



# --- Health Check ---
@app.get("/health")
async def health_check():
    health_status = {"status": "healthy"}

    # Database health
    if db_engine:
        try:
            with db_engine.connect() as conn:
                version = conn.execute(text("SELECT version()"))
                version_str = version.fetchone()[0]
                health_status["database"] = {"status": "healthy", "version": version_str.split(",")[0]}
        except Exception as e:
            health_status.update({"status": "degraded", "database_error": str(e)})

    # Model health
    health_status["ml_model"] = {"status": "loaded" if app.state.model and app.state.model.model else "missing"}

    return health_status

# --- Error Handlers ---
@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"Path {request.url.path} does not exist",
        },
    )

import traceback

@app.exception_handler(500)
async def server_error(request, exc):
    logger.error(f"❌ Server Error: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something broke! Check logs for details",
        },
    )
