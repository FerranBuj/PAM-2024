import os
import chromadb
from logutils import get_logger
from constants import (
    COLLECTION_PATH,
    COLLECTION_NAME,
    MATRIX_X,
    MATRIX_Y
)

logger = get_logger("db_utils")
class ChromaClientSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = chromadb.PersistentClient(path=COLLECTION_PATH)
        return cls._instance

def get_chroma_client():
    return ChromaClientSingleton.get_instance()

#db_debugging
if __name__ == "__main__":
    client = get_chroma_client()
    query = []
    for i in range(MATRIX_X * MATRIX_Y):
        query.append(((255 << 24) + (255 << 16) + (255 << 8) + (255)))
    logger.info(f"query color={query}")
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hsnw:space":"l2"}        
    )
    results = collection.query(
        query_embeddings=[query],
        n_results=1,
        include=["distances"] #ids are always returned
    )
    logger.info(f"query color={results}")