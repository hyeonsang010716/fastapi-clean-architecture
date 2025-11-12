from __future__ import annotations
from typing import List, Dict, Any, Optional
from pathlib import Path
import traceback
import asyncio
from functools import lru_cache
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.config.setting import settings
from app.core.logger import get_logger
from app.core.lock import get_redis_lock

logger = get_logger("chromaDB.manager")


class ChromaManager:
    """ChromaDB 벡터 스토어 관리자"""

    def __init__(self, persist_directory: str = "./data/chromadb-data"):
        self.embeddings: Optional[OpenAIEmbeddings] = None
        self.collections: Dict[str, Chroma] = {}
        self.persist_directory = persist_directory
        self.client: Optional[chromadb.PersistentClient] = None
        self._initialized = False
        self._lock = get_redis_lock()

    # ---------- 내부 유틸 ----------

    @staticmethod
    async def _to_thread(fn, *args, **kwargs):
        """동기 I/O를 안전하게 오프로딩"""
        return await asyncio.to_thread(fn, *args, **kwargs)


    def is_initialized(self) -> bool:
        return self._initialized and self.client is not None

    # ---------- 초기화 ----------

    async def initialize(self) -> bool:
        """ChromaDB 클라이언트/임베딩 초기화"""
        try:
            openai_api_key = settings.OPENAI_API_KEY
            if not openai_api_key:
                logger.warning("OpenAI API key not found, ChromaDB functionality will be limited")
                return False

            logger.info("임베딩 설정 중...")
            
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=openai_api_key,
                model="text-embedding-3-large",
            )

            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"ChromaDB 디렉토리 생성/확인 완료: {self.persist_directory}")

            self.client = await self._to_thread(chromadb.PersistentClient, self.persist_directory)

            self._initialized = True

            existing = await self._to_thread(self.client.list_collections)
            logger.info(f"기존 컬렉션 발견: {[c.name for c in existing]}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self._initialized = False
            return False

    # ---------- 컬렉션 관리 ----------

    async def list_collections(self) -> List[str]:
        """모든 컬렉션 목록"""
        if not self.is_initialized():
            logger.warning("ChromaDB not initialized")
            return []
        try:
            cols = await self._to_thread(self.client.list_collections)
            return [c.name for c in cols]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []


    async def delete_collection(self, collection_name: str) -> bool:
        """컬렉션 삭제"""
        if not self.is_initialized():
            logger.warning("ChromaDB not initialized")
            return False

        async with self._lock.lock(f"chroma:collection:{collection_name}", ttl=60) as acquired:
            if not acquired:
                logger.warning(f"Failed to acquire lock for deleting collection '{collection_name}'")
                return False
                
            try:
                self.collections.pop(collection_name, None)
                await self._to_thread(self.client.delete_collection, collection_name)
                logger.info(f"Collection '{collection_name}' 삭제 완료")
                return True
            except Exception as e:
                logger.error(f"Failed to delete collection '{collection_name}': {e}")
                return False


    async def get_or_create_collection(self, collection_name: str) -> Optional[Chroma]:
        """컬렉션 로드 또는 생성"""
        if not self.is_initialized():
            logger.warning("ChromaDB not initialized")
            return None

        if collection_name in self.collections:
            return self.collections[collection_name]

        async with self._lock.lock(f"chroma:collection:{collection_name}", ttl=60, timeout=10) as acquired:
            if not acquired:
                logger.warning(f"Failed to acquire lock for collection '{collection_name}'")
                return None
                
            if collection_name in self.collections:
                return self.collections[collection_name]

            try:
                def _build():
                    return Chroma(
                        embedding_function=self.embeddings,
                        persist_directory=self.persist_directory,
                        collection_name=collection_name,
                        client=self.client,
                    )

                vector_store = await self._to_thread(_build)
                self.collections[collection_name] = vector_store

                try:
                    count = await self._to_thread(vector_store._collection.count)
                    logger.info(f"Collection '{collection_name}' 생성/로드 완료. 문서 수: {count}")
                except Exception:
                    logger.info(f"Collection '{collection_name}' 생성/로드 완료.")

                return vector_store

            except Exception as e:
                logger.error(f"Failed to create/load collection '{collection_name}': {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None

    # ---------- 문서 CRUD ----------

    async def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any],
        collection_name: str,
    ) -> bool:
        """문서 추가"""
        vector_store = await self.get_or_create_collection(collection_name)
        if not vector_store:
            logger.warning(f"Collection '{collection_name}' not found")
            return False

        try:
            document = Document(page_content=content, metadata=metadata)
            await vector_store.aadd_documents(documents=[document], ids=[document_id])
            logger.info(f"Added document {document_id} to collection '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to add document to ChromaDB: {e}")
            return False


    async def delete_document(self, document_id: str, collection_name: str) -> bool:
        """문서 삭제"""
        vector_store = await self.get_or_create_collection(collection_name)
        if not vector_store:
            logger.warning(f"Collection '{collection_name}' not found")
            return False

        try:
            await vector_store.adelete(ids=[document_id])
            logger.info(f"Deleted document {document_id} from collection '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document from ChromaDB: {e}")
            return False


    async def update_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any],
        collection_name: str,
    ) -> bool:
        """문서 업데이트"""
        try:
            await self.delete_document(document_id, collection_name)
            return await self.add_document(document_id, content, metadata, collection_name)
        except Exception as e:
            logger.error(f"Failed to update document in ChromaDB: {e}")
            return False

    # ---------- 검색 ----------

    async def get_retriever(
        self,
        k: int,
        collection_name: str,
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Retriever 객체 반환"""
        vector_store = self.collections.get(collection_name)
        
        if not vector_store:
            vector_store = await self.get_or_create_collection(collection_name)

        kwargs = {"k": k}
        if search_kwargs:
            kwargs.update(search_kwargs)
        return vector_store.as_retriever(search_type=search_type, search_kwargs=kwargs)


    async def search(
        self,
        query: str,
        k: int,
        collection_name: str,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """유사도 검색"""
        vector_store = await self.get_or_create_collection(collection_name)
        if not vector_store:
            logger.warning(f"Collection '{collection_name}' not found")
            return []

        try:
            if filter:
                results = await vector_store.asimilarity_search(query=query, k=k, filter=filter)
            else:
                results = await vector_store.asimilarity_search(query=query, k=k)
            return results
        except Exception as e:
            logger.error(f"Failed to search in ChromaDB: {e}")
            return []

    # ---------- 통계/유틸 ----------

    async def get_document_count(self, collection_name: str) -> int:
        """저장된 문서 수"""
        vector_store = await self.get_or_create_collection(collection_name)
        if not vector_store:
            return 0
        try:
            return await self._to_thread(vector_store._collection.count)
        except Exception:
            return 0

    async def get_all_document_counts(self) -> Dict[str, int]:
        """모든 컬렉션의 문서 수"""
        counts: Dict[str, int] = {}
        names = await self.list_collections()
        for name in names:
            counts[name] = await self.get_document_count(name)
        return counts


@lru_cache(maxsize=1)
def get_chroma_manager() -> ChromaManager:
    """ChromaManager 싱글톤 인스턴스를 반환합니다."""
    return ChromaManager()