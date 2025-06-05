from fastapi import APIRouter
from app.schemas.learning import TrainingInput, TrainingResult

router = APIRouter()

@router.post("/train", response_model=TrainingResult)
def train_model(data: TrainingInput):
    # lógica mockada
    return TrainingResult(
        accuracy=0.95,
        message="Modelo treinado com sucesso."
    )
