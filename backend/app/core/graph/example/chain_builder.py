from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.graph.example.prompt_manager import PromptManager
from app.core.llm_manager import ModelName, get_llm_manager


class ChainManager:
    """다양한 체인을 구성하는 클래스"""
    
    def __init__(self, prompt_manager: PromptManager):
        self._prompt_manager = prompt_manager
        self._llm_manager = get_llm_manager()
        self._chains: Dict[str, Any] = {}
    
    
    def build_example_response_chain(self) -> Any:
        """예시 응답 체인을 생성합니다."""
        if 'example_response' not in self._chains:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._prompt_manager.get_prompt('example_response')),
                ("human", "[Question]\n{question}\n"),
            ])
            model = self._llm_manager.get_model(ModelName.GPT_4O_MINI)
            self._chains['example_response'] = prompt | model | StrOutputParser()
        
        return self._chains['example_response']
    
    
    def build_all_chains(self) -> None:
        """모든 체인을 생성합니다."""
        self.build_example_response_chain()
    
    
    def get_chain(self, chain_name: str) -> Optional[Any]:
        """특정 체인을 반환합니다."""
        return self._chains.get(chain_name)