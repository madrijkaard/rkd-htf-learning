from pydantic import BaseModel

class TrainingInput(BaseModel):
    epochs: int
    learning_rate: float

class TrainingResult(BaseModel):
    accuracy: float
    message: str
