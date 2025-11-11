from typing import Optional, Any, Dict, Tuple
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_community.callbacks import get_openai_callback
import aiosqlite
import time
import os

from app.core.graph.example.graph_state import GraphState
from app.core.graph.example.prompt_manager import PromptManager
from app.core.graph.example.chain_builder import ChainManager
from app.core.chroma_manager import get_chroma_manager
from app.util.agent_assistant import format_docs, format_retriever


class GraphOrchestrator:
    """LangGraph 오케스트레이터 클래스"""
    
    def __init__(
        self,
        prompt_manager: PromptManager,
        chain_manager: ChainManager,
        db_path: str = "./data/sqlite-data/example/sqlite.db"
    ):
        self._prompt_manager = prompt_manager
        self._chain_manager = chain_manager
        self.chromadb_manager = get_chroma_manager()
        self._db_path = db_path
        self._memory_saver: Optional[AsyncSqliteSaver] = None
        self._graph: Optional[Any] = None
        
        
    async def initialize(self) -> None:
        """그래프와 관련 컴포넌트를 초기화합니다."""
        
        # 모든 체인 빌드
        self._chain_manager.build_all_chains()
        
        # SQLite 메모리 세이버 초기화
        await self._init_sqlite_db()
        
        # 그래프 생성
        await self._build_graph()
    
    
    async def _init_sqlite_db(self) -> None:
        """SQLite 데이터베이스를 초기화합니다."""
        db_dir = os.path.dirname(self._db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = await aiosqlite.connect(self._db_path)
        conn.row_factory = aiosqlite.Row 
        self._memory_saver = AsyncSqliteSaver(conn)
        self._sqlite_conn = conn
    
    
    async def _retrieve_documents(self, state: GraphState) -> Dict[str, Any]:
        """문서를 검색합니다."""
        query = state["question"].content
            
        documents = await self.chromadb_manager.search(query, 15, collection_name="example_collection")
        
        return {"documents": documents}
    
    
    async def _example_response(self, state: GraphState) -> Dict[str, Any]:
        """응답을 생성합니다."""
        chain = self._chain_manager.get_chain('example_response')
        answer = await chain.ainvoke({
            "context": format_retriever(state["documents"]),
            "question": state["question"].content,
            "history": format_docs(state["messages"])
        })
        
        return {
            "answer": AIMessage(answer)
        }
        
        
    def _add_history_message(self, state: GraphState) -> Dict[str, Any]:
        """히스토리 메시지를 추가합니다."""
        
        return {"messages": [state['question'] , state['answer']]}
    
    
    async def _build_graph(self) -> None:
        """LangGraph를 구성합니다."""
        graph_builder = StateGraph(GraphState)
        
        # 노드 추가
        graph_builder.add_node("RetrieveDocument", self._retrieve_documents)
        graph_builder.add_node("ExampleResponse", self._example_response)
        graph_builder.add_node("AddHistoryMessage", self._add_history_message)
        
        # 엣지 추가
        graph_builder.add_edge(START, "RetrieveDocument")
        graph_builder.add_edge("RetrieveDocument", "ExampleResponse")
        graph_builder.add_edge("ExampleResponse", "AddHistoryMessage")
        graph_builder.add_edge("AddHistoryMessage", END)
        
        # 그래프 컴파일
        self._graph = graph_builder.compile(checkpointer=self._memory_saver)
        
    
    def get_graph(self) -> Any:
        """컴파일된 그래프를 반환합니다."""
        return self._graph
    
    
    async def ainvoke(
        self, 
        question: str, 
        session_id: str
    ) -> Tuple[str, float, int, float]:
        """그래프를 실행합니다.
        
        Returns:
            tuple: (answer, execution_time, total_tokens, total_cost)
        """
        input_data = {"question": HumanMessage(content=question)}
        config = {"configurable": {"thread_id": session_id}}
            
        start_time = time.perf_counter()
        
        with get_openai_callback() as cb:
            response = await self._graph.ainvoke(input_data, config)
        
        end_time = time.perf_counter()
    
        answer_content = response['answer'].content
        
        return (
            answer_content,
            end_time - start_time, 
            cb.total_tokens, 
            cb.total_cost
        )
    
    
    async def delete_memory(self, thread_id: str) -> None:
        """특정 스레드의 메모리를 삭제합니다."""
        
        try:
            async with self._graph.checkpointer.conn.execute(
                "DELETE FROM checkpoints WHERE thread_id = ?", 
                (thread_id,)
            ) as cursor:
                await self._graph.checkpointer.conn.commit()
        except Exception as e:
            raise
    
    async def cleanup(self) -> None:
        """리소스 정리"""
        if hasattr(self, '_sqlite_conn') and self._sqlite_conn:
            await self._sqlite_conn.close()
            self._sqlite_conn = None
    
    
prompt_manager = PromptManager()
chain_manager = ChainManager(prompt_manager)
example_graph = GraphOrchestrator(
    prompt_manager=prompt_manager,
    chain_manager=chain_manager,
    db_path="./data/sqlite-data/example/sqlite.db"
)