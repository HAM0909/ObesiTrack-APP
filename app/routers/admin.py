from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.schemas.user import UserResponse, UserUpdate, UserWithPredictions
from app.auth.dependencies import get_current_admin_user
from sqlalchemy import func, desc

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Numéro de page"),
    per_page: int = Query(20, ge=1, le=100, description="Nombre d'utilisateurs par page"),
    search: Optional[str] = Query(None, description="Recherche par email")
):
    """
    Récupérer la liste de tous les utilisateurs (admin uniquement)
    """
    query = db.query(User)
    
    # Filtrer par email si recherche
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    
    # Exclure l'administrateur actuel de la liste
    query = query.filter(User.id != current_admin.id)
    
    # Pagination
    offset = (page - 1) * per_page
    users = query.order_by(User.created_at.desc()).offset(offset).limit(per_page).all()
    
    return users

@router.get("/users/{user_id}", response_model=UserWithPredictions)
async def get_user_detail(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer les détails d'un utilisateur avec ses prédictions (admin uniquement)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour un utilisateur (admin uniquement)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Vérifier si l'email existe déjà
    if user_update.email and user_update.email != user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
    
    # Mettre à jour les champs
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Supprimer un utilisateur et toutes ses prédictions (admin uniquement)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Empêcher la suppression de son propre compte
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer votre propre compte"
        )
    
    # Supprimer l'utilisateur (les prédictions seront supprimées en cascade)
    db.delete(user)
    db.commit()
    
    return {"message": f"Utilisateur {user.email} supprimé avec succès"}

@router.get("/users/{user_id}/predictions")
async def get_user_predictions(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    """
    Récupérer les prédictions d'un utilisateur spécifique (admin uniquement)
    """
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Pagination
    offset = (page - 1) * per_page
    
    predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(
        Prediction.created_at.desc()
    ).offset(offset).limit(per_page).all()
    
    total = db.query(Prediction).filter(Prediction.user_id == user_id).count()
    
    return {
        "user": {"id": user.id, "email": user.email},
        "predictions": predictions,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/stats/dashboard")
async def get_admin_dashboard_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer les statistiques générales pour le dashboard admin
    """
    # Statistiques générales
    total_users = db.query(User).count()
    total_predictions = db.query(Prediction).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    # Utilisateurs récents (derniers 7 jours)
    from datetime import datetime, timedelta
    recent_date = datetime.utcnow() - timedelta(days=7)
    recent_users = db.query(User).filter(User.created_at >= recent_date).count()
    
    # Prédictions par catégorie
    prediction_categories = db.query(
        Prediction.prediction,
        func.count(Prediction.id).label('count')
    ).group_by(Prediction.prediction).all()
    
    # Utilisateurs les plus actifs
    active_users_stats = db.query(
        User.email,
        func.count(Prediction.id).label('prediction_count')
    ).join(
        Prediction, User.id == Prediction.user_id
    ).group_by(
        User.id, User.email
    ).order_by(
        desc(func.count(Prediction.id))
    ).limit(5).all()
    
    # Prédictions par jour (derniers 30 jours)
    from sqlalchemy import cast, Date
    daily_predictions = db.query(
        cast(Prediction.created_at, Date).label('date'),
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= datetime.utcnow() - timedelta(days=30)
    ).group_by(
        cast(Prediction.created_at, Date)
    ).order_by('date').all()
    
    return {
        "overview": {
            "total_users": total_users,
            "total_predictions": total_predictions,
            "active_users": active_users,
            "admin_users": admin_users,
            "recent_users": recent_users
        },
        "prediction_categories": [
            {"category": cat.prediction, "count": cat.count}
            for cat in prediction_categories
        ],
        "top_users": [
            {"email": user.email, "predictions": user.prediction_count}
            for user in active_users_stats
        ],
        "daily_predictions": [
            {"date": pred.date.isoformat(), "count": pred.count}
            for pred in daily_predictions
        ]
    }

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activer/désactiver un utilisateur (admin uniquement)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Empêcher la désactivation de son propre compte
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de modifier le statut de votre propre compte"
        )
    
    # Basculer le statut
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    status_text = "activé" if user.is_active else "désactivé"
    return {
        "message": f"Utilisateur {user.email} {status_text}",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active
        }
    }

@router.post("/users/{user_id}/make-admin")
async def toggle_admin_status(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Promouvoir/rétrograder un utilisateur en tant qu'admin
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Empêcher la modification de ses propres droits
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de modifier vos propres droits administrateur"
        )
    
    # Basculer le statut admin
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    
    status_text = "promu administrateur" if user.is_admin else "rétrogradé utilisateur"
    return {
        "message": f"Utilisateur {user.email} {status_text}",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }