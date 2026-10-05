from fastapi import APIRouter, Request

from app.schemas.extract import AfterSalesResult, ExtractRequest


router = APIRouter()


@router.post("/api/extract", response_model=AfterSalesResult)
async def extract(payload: ExtractRequest, request: Request) -> AfterSalesResult:
    return await request.app.state.extraction_service.extract(payload.text)
