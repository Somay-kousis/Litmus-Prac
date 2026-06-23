import os
from pathlib import Path
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Directory containing locally stored RAG document sheets
DOC_DIR = Path(__file__).resolve().parent / 'data' / 'rag_docs'

class SimpleRAG:
    def __init__(self):
        self.chunks = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.load_and_index_documents()

    def load_and_index_documents(self):
        if not os.path.exists(DOC_DIR):
            return
            
        raw_documents = []
        for file in os.listdir(DOC_DIR):
            if file.endswith('.txt'):
                filepath = DOC_DIR / file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    raw_documents.append((file, content))

        # Chunk documents by paragraphs/blocks
        self.chunks = []
        for filename, content in raw_documents:
            # Split by double newlines or clean breaks
            parts = content.split('\n\n')
            for part in parts:
                clean_part = part.strip()
                if clean_part and len(clean_part) > 20: # filter too short snippets
                    self.chunks.append(f"[{filename}] {clean_part}")

        if self.chunks:
            # Build local sparse vector representations of document chunks
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)

    def retrieve(self, query: str, k: int = 1) -> List[str]:
        if not self.chunks or self.tfidf_matrix is None:
            return []

        # Vectorize incoming query
        query_vec = self.vectorizer.transform([query])
        
        # Calculate Cosine Similarity via dot product (since TF-IDF vectors are L2-normalized)
        similarities = query_vec.dot(self.tfidf_matrix.T).toarray()[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:k]
        
        # Filter out zero-similarity results (meaningless matches)
        matches = []
        for idx in top_indices:
            if similarities[idx] > 0.05: # threshold to keep results relevant
                matches.append(self.chunks[idx])
                
        return matches

# Instantiated single instance of retriever
rag_engine = SimpleRAG()

def retrieve_car_context(query: str, k: int = 1) -> str:
    """Helper method to run RAG search and format retrieved context as string block."""
    results = rag_engine.retrieve(query, k)
    if not results:
        return "No additional reference documents retrieved."
    return "\n\n".join(results)
