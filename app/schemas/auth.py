from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .user import UserResponse

class Token(BaseModel):
    """Schéma pour le token JWT"""
    access_token: str = Field(..., description="Token d'accès JWT")
    token_type: str = Field(default="bearer", description="Type de token")

class TokenData(BaseModel):
    """Données contenues dans le token"""
    email: Optional[str] = None

class LoginRequest(BaseModel):
    """Schéma pour la connexion"""
    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(..., description="Mot de passe")

class LoginResponse(BaseModel):
    """Schéma de réponse pour la connexion"""
    access_token: str
    token_type: str
    user: UserResponse
    message: str

class RegisterResponse(BaseModel):
    """Schéma de réponse pour l'inscription"""
    user: UserResponse
    message: str
