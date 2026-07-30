"""Prediction history endpoints."""
from fastapi import APIRouter, Depends, Query

from app.schemas.history_schema import HistoryListResponse, HistoryRecordResponse
from app.services.history_service import HistoryService, get_history_service

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=HistoryListResponse, summary="List recent predictions")
async def list_history(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    history_service: HistoryService = Depends(get_history_service),
) -> HistoryListResponse:
    items, total = await history_service.list_recent(limit=limit, skip=skip)
    return HistoryListResponse(total=total, items=items)


@router.get("/{record_id}", response_model=HistoryRecordResponse, summary="Get a single prediction record")
async def get_history_record(
    record_id: str,
    history_service: HistoryService = Depends(get_history_service),
) -> HistoryRecordResponse:
    document = await history_service.get_by_id(record_id)
    return HistoryRecordResponse(**document)
