from pydantic import BaseModel, Field
from typing import Dict, Any

class PredictionResponse(BaseModel):
    predicted_category: str = Field(..., description='Predicted insurance category for the user', example='medium')
    probabilities: Dict[str, float] = Field(..., description='Probabilities for each class', example={'low': 0.1, 'medium': 0.7, 'high': 0.2})
    confidence: float = Field(..., description='Confidence of the prediction', example=0.7)
