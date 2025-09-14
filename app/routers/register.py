from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
import hashlib
import sys
from app.models import user
from app.database import get_db

# Ajout du chemin projet dans sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

router = APIRouter(tags=["authentication"])  # **Pas de prefix ici**

TEMPLATES_DIR = project_root / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.get("/register", response_class=HTMLResponse)
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        existing_user = db.query(user.User).filter(user.User.email == email).first()
        if existing_user:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Cet email est déjà enregistré"}
            )

        hashed_password = hash_password(password)

        new_user = user.User(
            email=email,
            username=username,
            password=hashed_password,
            is_active=True,
            is_admin=False
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return templates.TemplateResponse(
            "register.html",
            {"request": request, "success": "Utilisateur enregistré avec succès"}
        )

    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": f"Erreur lors de l'enregistrement: {str(e)}"}
        )
