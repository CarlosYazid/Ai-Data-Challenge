from pydantic import BaseModel, Field
from typing import Literal

CategoryLiteral = Literal["Cardiovascular", "Neurological", "Hepatorenal", "Oncological"]

class ResponseModel(BaseModel):
    
    category: CategoryLiteral
    confidence: float = Field(...)
    rationale: str = Field(...)

class QueryModel(BaseModel):
    
    title : str = Field(...)
    abstract : str = Field(...)