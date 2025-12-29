# chat/rag_core/vector_store.py

import numpy as np
from typing import List, Tuple

# In-memory storage for the RAG system: [vector, text_chunk]
# For this classification project, we only store one main knowledge chunk.
KNOWLEDGE_STORE: List[Tuple[np.ndarray, str]] = []


def initialize_vector_store(knowledge_vector: np.ndarray, knowledge_text: str):
    """
    Initializes the in-memory vector store with the primary knowledge base
    embedding and text.
    """
    if knowledge_vector is not None and knowledge_text:
        # Clear existing data and add the new knowledge chunk
        global KNOWLEDGE_STORE
        KNOWLEDGE_STORE = [(knowledge_vector, knowledge_text)]
        print(f"Vector store initialized with 1 knowledge chunk (Dimension: {knowledge_vector.shape[0]})")
    else:
        print("Vector store initialization failed due to missing vector or text.")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculates the cosine similarity between two vectors."""
    # Ensure vectors are non-zero to avoid division by zero
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_context(query_vector: np.ndarray, top_k: int = 1) -> str:
    """
    Retrieves the most relevant context from the vector store based on the query.
    For classification, we expect the entire knowledge base to be relevant.
    """
    if not KNOWLEDGE_STORE:
        return ""  # No context available

    similarities = []
    for vector, text in KNOWLEDGE_STORE:
        similarity = cosine_similarity(query_vector, vector)
        similarities.append((similarity, text))

    # Since we only have one chunk, we always return it, regardless of similarity
    # In a real RAG, this would sort and concatenate top_k results.

    # Sort and take the top_k relevant texts
    # relevant_chunks = sorted(similarities, key=lambda x: x[0], reverse=True)[:top_k]
    # return "\n---\n".join([text for _, text in relevant_chunks])

    # For this project: just return the main knowledge base text
    return KNOWLEDGE_STORE[0][1]
