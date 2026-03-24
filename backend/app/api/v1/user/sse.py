from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.service.progress import ProgressService

router = APIRouter(prefix="/sse", tags=["SSE-Progress"])

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@router.get(
    "/chat",
    summary="진행률 SSE 스트림",
    description="10초 단위로 총 5단계의 진행률을 SSE로 전송합니다."
)
async def chat(
    user_id: str = Query(..., min_length=1, description="사용자 ID")
):
    """SSE 진행률 스트림 시작"""
    return StreamingResponse(
        ProgressService.start_progress(user_id),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@router.get(
    "/search",
    summary="진행률 이어보기 SSE 스트림",
    description="사용자의 현재 진행률을 조회하고, 진행 중이면 SSE로 이어서 스트리밍합니다."
)
async def search_progress(
    user_id: str = Query(..., min_length=1, description="사용자 ID")
):
    """사용자 진행률 이어보기"""
    return StreamingResponse(
        ProgressService.search_progress(user_id),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
