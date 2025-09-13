from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.database import get_db
from app.schemas.prediction import (
    PredictionInput,
    PredictionResponse,
    PredictionHistory,
)
from app.ml.predictor import load_model
from app.auth.dependencies import get_current_user
from app.models import User, Prediction
from app.ml.predictor import ObesityPredictor

logger = logging.getLogger(__name__)
router = APIRouter()

# Globals (consider dependency injection for production)
model = load_model()  # Load at startup


@router.post("/predict", response_model=PredictionResponse)
async def make_prediction(
    input_data: PredictionInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """Make obesity prediction based on input features."""
    global model

    if not model:
        logger.warning("Model not loaded at startup. Reloading...")
        model = load_model()
        if not model:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Prediction model is not available.",
            )

    try:
        # Convert input to dict (keys must match model requirements)
        features = input_data.dict()

        # Make prediction (ensure model.predict() expects dict format)
        result = model.predict(features)

        # Validate prediction result structure (optional)
        if not isinstance(result, dict):
            raise ValueError("Model returned invalid result format.")

        # Save prediction to DB
        db_prediction = Prediction(
            user_id=current_user.id,
            prediction=result["prediction"],
            probability=result["probability"],
            bmi=result["bmi"],
            risk_level=result["risk_level"],
            input_data=features,
            created_at=datetime.now(),
        )
        db.add(db_prediction)
        db.commit()

        # Build response with fallback defaults
        response = PredictionResponse(
            prediction=result["prediction"],
            probability=result["probability"],
            confidence=result.get("confidence", result["probability"]),  # Fallback
            bmi=result["bmi"],
            risk_level=result["risk_level"],
            recommendations=result.get("recommendations", []),  # Default empty list
            timestamp=datetime.now(),
        )

        logger.info(
            f"Prediction for user {current_user.id}: {result['prediction']} (Risk: {result['risk_level']})"
        )
        return response

    except KeyError as e:
        logger.error(f"Missing expected key in prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction result misses required field: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction system error: {str(e)}",
        )


@router.get("/history", response_model=List[PredictionHistory])
async def get_prediction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
) -> List[PredictionHistory]:
    """Get user's prediction history (limited to `limit` most recent)."""
    if limit < 1 or limit > 50:  # Basic validation
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit must be between 1 and 50.",
        )

    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .limit(limit)
        .all()
    )
    return predictions


@router.get("/model-status")
async def get_model_status() -> Dict[str, Any]:
    """Check model health and features."""
    global model

    if not model:
        model = load_model()
        if not model:
            logger.warning("Model unavailable despite reloaded attempt.")
            return {"status": "unavailable"}

    return {
        "model_loaded": model is not None,
        "has_random_forest": getattr(model, "model", None) is not None,
        "has_feature_encoder": getattr(model, "feature_encoder", None) is not None,
        "has_label_encoder": getattr(model, "label_encoder", None) is not None,
        "numerical_features": getattr(model, "numerical_features", []),
        "categorical_features": getattr(model, "categorical_features", []),
    }