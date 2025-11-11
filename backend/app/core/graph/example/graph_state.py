from typing import List, TypedDict, Annotated
from langchain_core.documents import Document
from langchain.messages import HumanMessage
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """LangGraph 상태 정의"""
    messages: Annotated[List, add_messages]     # 메시지 관리
    question: HumanMessage                      # 최신 질문
    documents: List[Document]                   # Retriever 문서 
    answer: str                                 # 최종 결과