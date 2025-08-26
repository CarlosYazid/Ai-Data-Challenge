from fastapi import APIRouter

from services import AgentService
from models import QueryModel, ResponseModel

router = APIRouter(prefix="/classify", tags=["agent"])

@router.post("/",response_model=ResponseModel)
async def classify_paper(query : QueryModel):
    return await AgentService.classify(query)