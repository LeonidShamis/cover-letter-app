import faiss
import numpy as np
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from src.config.settings import settings

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.index = None
        self.texts = []
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
    
    def add_documents(self, content: str) -> None:
        """Chunk, embed and store documents in FAISS"""
        chunks = self.text_splitter.split_text(content)
        self.texts.extend(chunks)
        
        # Get embeddings
        embeddings = self.embeddings.embed_documents(chunks)
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Create or update FAISS index
        if self.index is None:
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(embeddings_array)
    
    def similarity_search(self, query: str, k: int = 3) -> List[str]:
        """Search for similar documents"""
        if self.index is None or len(self.texts) == 0:
            return []
        
        query_embedding = self.embeddings.embed_query(query)
        query_array = np.array([query_embedding]).astype('float32')
        
        distances, indices = self.index.search(query_array, min(k, len(self.texts)))
        
        return [self.texts[i] for i in indices[0] if i < len(self.texts)]
