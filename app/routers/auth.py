from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, LoginResponse, RegisterResponse
from app.auth.jwt_handler import verify_password, get_password_hash, create_access_token
from app.auth.dependencies import get_current_active_user

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    
    # Vérifier si l'utilisateur existe déjà
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_admin=False  # Par défaut, les nouveaux utilisateurs ne sont pas admin
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return RegisterResponse(
        user={
            "id": db_user.id,
            "email": db_user.email,
            "is_admin": db_user.is_admin,
            "created_at": db_user.created_at
        },
        message="User registered successfully"
    )

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Connexion utilisateur"""
    
    # Vérifier l'utilisateur
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Créer le token d'accès
    access_token = create_access_token(data={"sub": user.email})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at
        },
        message="Login successful"
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Obtenir les informations de l'utilisateur connecté"""
    return current_user

@router.post("/logout")
async def logout():
    """Déconnexion utilisateur (côté client principalement)"""
    return {"message": "Logout successful. Please remove the token from client side."}