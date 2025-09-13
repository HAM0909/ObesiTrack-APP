from fastapi import APIRouter, HTTPException, status
import json
import os
from datetime import datetime
from app.ml.predictor import ObesityPredictor

router = APIRouter()

@router.get("/metrics")
async def get_model_metrics():
    """
    Récupérer les informations et métriques du modèle ML
    """
    try:
        # Charger les métriques depuis le fichier JSON
        metrics_path = "app/ml/metrics.json"
        
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
        else:
            metrics = {
                "error": "Métriques non trouvées",
                "message": "Le modèle n'a pas encore été entraîné"
            }
        
        # Informations sur le prédicteur
        predictor = ObesityPredictor()
        
        model_info = {
            "model_name": "ObesiTrack Random Forest Classifier",
            "model_type": "Classification multiclasse",
            "framework": "scikit-learn",
            "target_classes": [
                "Insufficient_Weight",
                "Normal_Weight", 
                "Overweight_Level_I",
                "Overweight_Level_II",
                "Obesity_Type_I",
                "Obesity_Type_II",
                "Obesity_Type_III"
            ],
            "features": [
                "Age", "Height", "Weight", "FCVC", "NCP", 
                "CAEC", "FAF", "TUE", "CALC", "MTRANS"
            ],
            "model_loaded": predictor.is_loaded,
            "last_updated": datetime.now().isoformat()
        }
        
        # Combiner les informations
        response = {
            **model_info,
            "performance_metrics": metrics
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des métriques: {str(e)}"
        )

@router.get("/metrics/health")
async def model_health_check():
    """
    Vérifier l'état de santé du modèle ML
    """
    predictor = ObesityPredictor()
    
    # Test basique de prédiction
    try:
        # Créer des données de test
        from app.schemas.prediction import PredictionInput, CAECEnum, CALCEnum, MTRANSEnum
        
        test_input = PredictionInput(
            age=25.0,
            height=1.70,
            weight=70.0,
            fcvc=2.0,
            ncp=3.0,
            caec=CAECEnum.sometimes,
            faf=1.0,
            tue=1.0,
            calc=CALCEnum.no,
            mtrans=MTRANSEnum.public_transportation
        )
        
        # Effectuer une prédiction de test
        result = predictor.predict(test_input)
        
        return {
            "status": "healthy",
            "model_loaded": predictor.is_loaded,
            "test_prediction": {
                "successful": True,
                "prediction": result["prediction"],
                "confidence": result["confidence"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "model_loaded": predictor.is_loaded,
            "error": str(e),
            "test_prediction": {
                "successful": False
            },
            "timestamp": datetime.now().isoformat()
        }

@router.get("/metrics/feature-importance")
async def get_feature_importance():
    """
    Récupérer l'importance des features du modèle
    """
    predictor = ObesityPredictor()
    
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle non chargé"
        )
    
    try:
        # Récupérer l'importance des features
        if hasattr(predictor.model, 'feature_importances_'):
            feature_importance = predictor.model.feature_importances_
            
            importance_dict = {}
            for i, importance in enumerate(feature_importance):
                feature_name = predictor.feature_names[i]
                importance_dict[feature_name] = float(importance)
            
            # Trier par importance décroissante
            sorted_importance = dict(
                sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            )
            
            return {
                "feature_importance": sorted_importance,
                "top_3_features": list(sorted_importance.keys())[:3],
                "total_features": len(sorted_importance),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "error": "Le modèle ne supporte pas l'importance des features",
                "model_type": type(predictor.model).__name__
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'importance des features: {str(e)}"
        )

@router.get("/metrics/prediction-distribution")
async def get_prediction_distribution():
    """
    Récupérer la distribution des prédictions (nécessite accès à la DB)
    """
    from app.database import get_db
    from app.models.prediction import Prediction
    from sqlalchemy import func
    from fastapi import Depends
    from sqlalchemy.orm import Session
    
    # Cette route nécessite une dépendance de DB, on va la rendre optionnelle
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        
        # Statistiques des prédictions
        distribution = db.query(
            Prediction.prediction,
            func.count(Prediction.id).label('count')
        ).group_by(Prediction.prediction).all()
        
        total_predictions = db.query(Prediction).count()
        
        distribution_data = []
        for item in distribution:
            percentage = (item.count / total_predictions) * 100 if total_predictions > 0 else 0
            distribution_data.append({
                "category": item.prediction,
                "count": item.count,
                "percentage": round(percentage, 2)
            })
        
        db.close()
        
        return {
            "total_predictions": total_predictions,
            "distribution": distribution_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": "Impossible de récupérer les statistiques de la base de données",
            "detail": str(e),
            "total_predictions": 0,
            "distribution": []
        }

@router.get("/metrics/model-info")
async def get_detailed_model_info():
    """
    Informations détaillées sur le modèle
    """
    predictor = ObesityPredictor()
    
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle non chargé"
        )
    
    try:
        model_info = {
            "model_type": type(predictor.model).__name__,
            "algorithm": "Random Forest",
            "is_loaded": predictor.is_loaded,
            "feature_count": len(predictor.feature_names),
            "class_count": len(predictor.target_classes),
            "features": predictor.feature_names,
            "target_classes": predictor.target_classes,
            "encoders": {
                name: list(encoder.classes_) 
                for name, encoder in predictor.label_encoders.items()
            }
        }
        
        # Paramètres du modèle si disponibles
        if hasattr(predictor.model, 'get_params'):
            model_info["parameters"] = predictor.model.get_params()
        
        return model_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des informations du modèle: {str(e)}"
        )