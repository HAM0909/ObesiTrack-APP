import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

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
    logger.info(f"📊 Connected to: {os.getenv('DATABASE_URL').split('@')[1]}")
except ImportError as e:
    logger.error(f"❌ Failed to import database module: {e}")
    raise SystemExit("Database initialization critical failure") from e  # Exit if critical
except Exception as e:
    logger.error(f"❌ Database connectivity failed: {e}")
    raise SystemExit("Database not available") from e

# --- Model Loading ---
model = None
try:
    from app.ml.predictor import load_model # Corrected import path
    model = load_model()
    if model:
        logger.info("✅ ML model loaded successfully")
    else:
        logger.warning("⚠️ ML model file missing, using fallback...")
except ImportError as e:
    logger.warning(f"⚠️ ML model module not found: {e}")
except Exception as e:
    logger.error(f"❌ ML model initialization failed: {e}")

# --- FastAPI App Initialization ---
app = FastAPI(
    title=os.getenv("APP_NAME", "ObesiTrack"),
    description="Obesity Tracking & Prediction System",
    version=os.getenv("APP_VERSION", "1.0.0"),
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Static Files Setup ---
STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
logger.info(f"✅ Static files mounted from {STATIC_DIR}")
logger.info(f"✅ Templates configured from {TEMPLATES_DIR}")

# --- CORS Configuration ---
APP_ORIGINS = [
    "http://localhost:3000",  # React default
    "http://localhost:5173",  # Vite default
    "http://localhost:8080",  # Common alternate
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=APP_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Router Imports (Graceful Failure) ---
ROUTERS = [
    ("auth", "Authentication"),
    ("prediction", "Predictions"),
    ("metrics", "Dashboard"),
    ("pages", "Pages"),
]

for router_path, tag in ROUTERS:
    try:
        module = __import__(f"app.routers.{router_path}", fromlist=["router"])
        if router_path == "pages":
            app.include_router(module.router, tags=[tag])
            logger.info(f"✅ Router loaded: /{router_path}")
        else:
            app.include_router(module.router, prefix=f"/api/{router_path}", tags=[tag])
            logger.info(f"✅ Router loaded: /api/{router_path}")
    except ImportError as e:
        logger.warning(f"⚠️ Router {router_path} not found: {e}")
    except Exception as e:
        logger.error(f"❌ Router {router_path} failed to load: {e}")

# --- Root Endpoint ---
@app.get("/")
def root():
    return {
        "application": os.getenv("APP_NAME", "ObesiTrack"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
        },
        "api_paths": {
            f"/api/{r}": f"/{r} operations" for _, r in ROUTERS
        },
    }

# --- Health Check ---
@app.get("/health")
async def health_check():
    health_status = {"status": "healthy"}

    # Database health
    if db_engine:
        try:
            with db_engine.connect() as conn:
                version = conn.execute("SELECT version()").fetchone()[0]
                health_status["database"] = {"status": "healthy", "version": version.split(",")[0]}
        except Exception as e:
            health_status.update({"status": "degraded", "database_error": str(e)})

    # Model health
    health_status["ml_model"] = {"status": "loaded" if model else "missing"}

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

@app.exception_handler(500)
async def server_error(request, exc):
    logger.error(f"❌ Server Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something broke! Check logs for details",
        },
    )

# --- Startup/Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info(f"🚀 {os.getenv('APP_NAME', 'ObesiTrack')} v{os.getenv('APP_VERSION', '1.0.0')} Starting")
    logger.info(f"📝 Docs: http://localhost:8000/docs")
    logger.info(f"🐘 DB: {bool(db_engine)}")
    logger.info(f"🤖 ML: {bool(model)}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Shutting down...")
    if db_engine:
        db_engine.dispose()
        logger.info("Database connections closed")

# --- Development Server ---
if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000
    RELOAD = os.getenv("DEBUG", "False").lower() == "true"

    logger.info(f"Starting on {HOST}:{PORT} (Debug={RELOAD})")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="debug" if RELOAD else "info",
    )