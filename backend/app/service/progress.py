import json
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any

from app.core.logger import get_logger
from app.core.redis import RedisClient
from app.repository.progress import ProgressRepository
from app.util.id_generator import generate_progress_id

logger = get_logger("progress_service")

# Redis TTL 상수
PROGRESS_TTL = 300  # 5분

# 진행 단계 정의
PROGRESS_STEPS = [
    {"step": 1, "message": "요청 접수 완료"},
    {"step": 2, "message": "데이터 수집 중..."},
    {"step": 3, "message": "데이터 분석 중..."},
    {"step": 4, "message": "결과 생성 중..."},
    {"step": 5, "message": "처리 완료"},
]


class ProgressService:
    """진행률 관리 서비스"""

    # 실행 중인 백그라운드 태스크 관리
    _running_tasks: Dict[str, asyncio.Task] = {}

    @staticmethod
    def _redis_key(progress_key: str) -> str:
        """Redis 키 생성"""
        return f"progress:{progress_key}"

    @staticmethod
    async def _update_redis(progress_key: str, step_data: Dict[str, Any]) -> None:
        """Redis에 진행률 업데이트"""
        client = await RedisClient.get_client()
        key = ProgressService._redis_key(progress_key)
        await client.set(key, json.dumps(step_data), ex=PROGRESS_TTL)

    @staticmethod
    async def _get_redis(progress_key: str) -> Optional[Dict[str, Any]]:
        """Redis에서 진행률 조회"""
        client = await RedisClient.get_client()
        key = ProgressService._redis_key(progress_key)
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    async def _delete_redis(progress_key: str) -> None:
        """Redis에서 진행률 삭제"""
        client = await RedisClient.get_client()
        key = ProgressService._redis_key(progress_key)
        await client.delete(key)

    @staticmethod
    async def _run_progress(user_id: str, progress_key: str) -> None:
        """백그라운드에서 실행되는 실제 진행 작업 (SSE 연결과 독립적)"""
        try:
            for step_info in PROGRESS_STEPS:
                await asyncio.sleep(10)  # 10초 간격

                step_data = {
                    "progress_key": progress_key,
                    "user_id": user_id,
                    "current_step": step_info["step"],
                    "total_steps": len(PROGRESS_STEPS),
                    "message": step_info["message"],
                    "status": "in_progress" if step_info["step"] < len(PROGRESS_STEPS) else "completed"
                }

                await ProgressService._update_redis(progress_key, step_data)

                logger.bind(
                    progress_key=progress_key,
                    step=step_info["step"]
                ).debug("진행률 업데이트")

            # 완료 처리: MongoDB 먼저 업데이트 → Redis 삭제
            await ProgressRepository.update_end_status(progress_key, end=True)
            await ProgressService._delete_redis(progress_key)
            logger.bind(progress_key=progress_key).info("진행률 추적 완료")

        except Exception as e:
            logger.bind(progress_key=progress_key, error=str(e)).error("진행률 처리 중 오류")
            await ProgressRepository.update_end_status(progress_key, end=False)
            await ProgressService._delete_redis(progress_key)
        finally:
            ProgressService._running_tasks.pop(progress_key, None)

    @staticmethod
    async def _poll_progress(progress_key: str, user_id: str) -> AsyncGenerator[str, None]:
        """Redis를 폴링하며 진행률 변경 시 SSE 이벤트 전송"""
        last_step = -1

        while True:
            await asyncio.sleep(2)  # 2초 간격 폴링

            current_data = await ProgressService._get_redis(progress_key)

            if not current_data:
                # Redis에서 사라짐 → MongoDB에서 최종 상태 확인
                progress = await ProgressRepository.find_by_key(progress_key)

                if progress and progress.end is True:
                    data = json.dumps({
                        "progress_key": progress_key,
                        "user_id": user_id,
                        "status": "completed",
                        "message": "처리 완료"
                    })
                    yield f"event: done\ndata: {data}\n\n"
                else:
                    # end=None 또는 end=False → 실패
                    if progress and progress.end is None:
                        await ProgressRepository.update_end_status(progress_key, end=False)
                    data = json.dumps({
                        "progress_key": progress_key,
                        "user_id": user_id,
                        "status": "failed",
                        "message": "서버 비정상 종료로 인해 진행이 실패했습니다"
                    })
                    yield f"event: failed\ndata: {data}\n\n"
                return

            current_step = current_data.get("current_step", -1)

            # 단계가 변경되었을 때만 이벤트 전송
            if current_step != last_step:
                yield f"event: progress\ndata: {json.dumps(current_data)}\n\n"
                last_step = current_step

            # 완료 상태면 종료
            if current_data.get("status") == "completed":
                return

    @staticmethod
    async def start_progress(user_id: str) -> AsyncGenerator[str, None]:
        """SSE 진행률 스트림 시작 (/chat)"""
        progress_key = generate_progress_id()

        # MongoDB + Redis 초기 상태를 동시에 생성 (둘 다 존재해야 /search가 안전)
        await asyncio.gather(
            ProgressRepository.create(user_id=user_id, progress_key=progress_key),
            ProgressService._update_redis(progress_key, {
                "progress_key": progress_key,
                "user_id": user_id,
                "current_step": 0,
                "total_steps": len(PROGRESS_STEPS),
                "message": "대기 중...",
                "status": "in_progress"
            })
        )
        logger.bind(user_id=user_id, progress_key=progress_key).info("진행률 추적 시작")

        # 백그라운드 태스크로 실제 작업 실행 (SSE 연결과 독립적)
        task = asyncio.create_task(
            ProgressService._run_progress(user_id, progress_key)
        )
        ProgressService._running_tasks[progress_key] = task

        # 초기 이벤트: progress_key 전달
        init_data = json.dumps({
            "progress_key": progress_key,
            "user_id": user_id,
            "total_steps": len(PROGRESS_STEPS),
            "status": "started"
        })
        yield f"event: init\ndata: {init_data}\n\n"

        # Redis 폴링으로 진행률 스트리밍
        async for event in ProgressService._poll_progress(progress_key, user_id):
            yield event

    @staticmethod
    async def search_progress(user_id: str) -> AsyncGenerator[str, None]:
        """사용자의 진행률 이어보기 SSE 스트림 (/search)"""
        # MongoDB에서 진행 중인(end=None) 레코드 조회
        progress = await ProgressRepository.find_active_by_user(user_id)

        if not progress:
            data = json.dumps({"user_id": user_id, "status": "no_active_progress"})
            yield f"event: done\ndata: {data}\n\n"
            return

        progress_key = progress.progress_key

        # Redis에서 현재 진행 상태 조회
        redis_data = await ProgressService._get_redis(progress_key)

        if not redis_data:
            # end=None인데 Redis에도 없음 → 서버 비정상 종료로 인한 실패
            await ProgressRepository.update_end_status(progress_key, end=False)
            logger.bind(
                user_id=user_id,
                progress_key=progress_key
            ).warning("Redis 데이터 없음 - 실패 처리")

            data = json.dumps({
                "user_id": user_id,
                "progress_key": progress_key,
                "status": "failed",
                "message": "서버 비정상 종료로 인해 진행이 실패했습니다"
            })
            yield f"event: failed\ndata: {data}\n\n"
            return

        # 현재 상태를 resume 이벤트로 즉시 전송
        yield f"event: resume\ndata: {json.dumps(redis_data)}\n\n"

        # 이미 완료 상태면 종료
        if redis_data.get("status") == "completed":
            return

        # Redis 폴링으로 나머지 진행률 이어서 스트리밍
        async for event in ProgressService._poll_progress(progress_key, user_id):
            yield event
