from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.jwt_handler import verify_token
from typing import Optional

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Obtenir l'utilisateur actuel à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extraire le token
    token = credentials.credentials
    
    # Vérifier et décoder le token
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    
    # Récupérer l'utilisateur de la base de données
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtenir l'utilisateur actuel et vérifier qu'il est actif"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Obtenir l'utilisateur actuel et vérifier qu'il est administrateur"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Obtenir l'utilisateur actuel à partir du token dans les cookies ou headers"""
    token = None
    
    # Essayer d'abord les cookies (pour les pages web)
    if hasattr(request, 'cookies'):
        token = request.cookies.get("access_token")
    
    # Si pas de cookie, essayer l'en-tête Authorization
    if not token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    # Si toujours pas de token, essayer localStorage via JavaScript (simulation)
    if not token:
        return None
    
    # Vérifier et décoder le token
    email = verify_token(token)
    if email is None:
        return None
    
    # Récupérer l'utilisateur de la base de données
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        return None
    
    return user

def get_current_admin_user_web(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Obtenir l'utilisateur admin pour les pages web (avec gestion des cookies)"""
    user = get_current_user_from_cookie(request, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user