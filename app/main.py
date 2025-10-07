import logging
import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import init_db
from app.routers import prediction, auth, metrics, admin
from app.auth.dependencies import get_current_admin_user_web
from app.models.user import User
from app.ml.predictor import ObesityPredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the static folder path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
static_folder = os.path.join(parent_dir, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=static_folder), name="static")
logger.info(f"✅ Static files mounted from {static_folder}")

# Initialize templates (templates are stored in project-level templates folder)
TEMPLATES_DIR = os.path.join(parent_dir, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include routers
app.include_router(prediction.router, prefix="/api/prediction", tags=["predictions"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(admin.router, tags=["admin"])

# Initialize database
@app.on_event("startup")
async def startup():
    logger.info("🚀 Application starting up...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized successfully")
    
    # Initialize ML model
    try:
        predictor = ObesityPredictor()
        # Verify model is loaded
        if not predictor.model:
            raise RuntimeError("Model failed to load properly")
        app.state.model = predictor
        logger.info("✅ ML model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Error loading ML model: {str(e)}", exc_info=True)
        raise

    
@app.on_event("shutdown")
async def shutdown():
    logger.info("👋 Shutting down...")
    logger.info("Database connections closed")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/app")
async def app_page(request: Request):
    logger.info("Incoming request: GET /app")
    return templates.TemplateResponse("app_obesity.html", {"request": request})

@app.get("/history")
async def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/admin")
async def admin_page(request: Request):
    """
    Page d'administration avec vérification des permissions côté client
    """
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}