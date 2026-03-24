import uuid
from datetime import datetime
from typing import Tuple

def generate_id() -> Tuple[int,str]:
    timestamp = int(datetime.now().timestamp())
    unique_part = uuid.uuid4().hex[:8]
    return timestamp, unique_part


def generate_store_id() -> str:
    """가게 고유 ID 생성"""
    timestamp, unique_part = generate_id()
    return f"STR_{timestamp}_{unique_part}"


def generate_product_id() -> str:
    """상품 고유 ID 생성"""
    timestamp, unique_part = generate_id()
    return f"PRD_{timestamp}_{unique_part}"


def generate_payment_id() -> str:
    """결제 고유 ID 생성"""
    timestamp, unique_part = generate_id()
    return f"PAY_{unique_part}_{timestamp}"


def generate_progress_id() -> str:
    """진행률 고유 키 생성"""
    timestamp, unique_part = generate_id()
    return f"PGS_{timestamp}_{unique_part}"