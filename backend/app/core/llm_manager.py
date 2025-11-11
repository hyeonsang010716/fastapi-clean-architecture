from typing import Dict, List
from langchain_openai import ChatOpenAI
from enum import Enum

from app.config.setting import settings


class ModelName(str, Enum):
    """사용 가능한 모델 이름"""
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_5 = "gpt-5"
    
    @classmethod
    def values(cls) -> List[str]:
        """모든 모델 이름을 리스트로 반환"""
        return [model.value for model in cls]


class LLMManager:
    """LLM 모델을 관리하는 클래스"""
    
    _models: Dict[str, ChatOpenAI] = {}
    _initialized: bool = False
    
    def __init__(self):
        raise RuntimeError("LLMManager는 인스턴스를 생성할 수 없습니다.")
    
    @classmethod
    def _initialize(cls) -> None:
        """모든 LLM 모델을 초기화합니다."""
        if not cls._initialized:
            for model in ModelName:
                cls._models[model.value] = ChatOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    model=model.value
                )
            cls._initialized = True
    
    @classmethod
    def get_model(cls, model_name: str) -> ChatOpenAI:
        """모델 이름으로 LLM 모델을 반환합니다."""
        if not cls._initialized:
            cls._initialize()
        
        if model_name not in cls._models:
            raise ValueError(
                f"Model '{model_name}' not found. "
                f"Available models: {', '.join(ModelName.values())}"
            )
        
        return cls._models[model_name]
    
    @classmethod
    def is_initialized(cls) -> bool:
        """초기화 상태를 반환합니다."""
        return cls._initialized


def initialize_llm_manager() -> None:
    """LLM Manager 초기화 함수"""
    LLMManager._initialize()

def check_llm_model(model_name: str) -> bool:
    """사용 가능한 LLM 모델인지 체크하는 함수"""
    return model_name in ModelName.values()


def get_llm_model(model: ModelName) -> ChatOpenAI:
    """모델 가져오기"""
    return LLMManager.get_model(model.value)