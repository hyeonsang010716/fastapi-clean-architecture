from typing import Dict, List, Optional
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
    
    _instance: Optional['LLMManager'] = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._models: Dict[str, ChatOpenAI] = {}
        self._initialized = False
    
    def initialize(self) -> bool:
        """모든 LLM 모델을 초기화합니다."""
        if not self._initialized:
            for model in ModelName:
                self._models[model.value] = ChatOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    model=model.value
                )
            self._initialized = True
        
        return self._initialized
    
    def get_model(self, model_name: str) -> ChatOpenAI:
        """모델 이름으로 LLM 모델을 반환합니다."""
        if not self._initialized:
            self.initialize()
        
        if model_name not in self._models:
            raise ValueError(
                f"Model '{model_name}' not found. "
                f"Available models: {', '.join(ModelName.values())}"
            )
        
        return self._models[model_name]
    
    def is_initialized(self) -> bool:
        """초기화 상태를 반환합니다."""
        return self._initialized


def get_llm_manager() -> LLMManager:
    """LLMManager 싱글톤 인스턴스를 반환합니다."""
    return LLMManager()