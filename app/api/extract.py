from fastapi import APIRouter, Request

from app.schemas.extract import AfterSalesResult, ExtractRequest


router = APIRouter()


# 将已校验的用户文本交给售后抽取服务，返回结构化结果。
@router.post("/api/extract", response_model=AfterSalesResult)
async def extract(payload: ExtractRequest, request: Request) -> AfterSalesResult:
    return await request.app.state.extraction_service.extract(payload.text)
