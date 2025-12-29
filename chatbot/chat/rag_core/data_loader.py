# chat/rag_core/data_loader.py

import os
import numpy as np
from google import genai
from google.genai.errors import APIError
from django.conf import settings

# --- Initialize Gemini Client for Embedding ---
try:
    EMBEDDING_CLIENT = genai.Client(api_key=settings.GEMINI_API_KEY)
    EMBEDDING_MODEL = 'text-embedding-004'  # A reliable embedding model
except Exception as e:
    print(f"Embedding Client Initialization Error: {e}")
    EMBEDDING_CLIENT = None


def get_embedding(text: str) -> np.ndarray | None:
    """Generates an embedding vector for a given text using the Gemini API."""
    if not EMBEDDING_CLIENT:
        return None

    try:
        response = EMBEDDING_CLIENT.models.embed_content(
            model=EMBEDDING_MODEL,
            content=[text],
            task_type="RETRIEVAL_DOCUMENT"  # Use appropriate task type
        )
        # The result is a list of embeddings; we take the first one
        return np.array(response['embedding'][0])
    except APIError as e:
        print(f"Gemini Embedding API Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Embedding Error: {e}")
        return None


def load_knowledge_base(knowledge_text: str) -> tuple[np.ndarray | None, str]:
    """
    Loads the primary knowledge text, generates its embedding, and prepares
    it for the vector store.
    """
    print("Generating embedding for the primary knowledge base...")
    vector = get_embedding(knowledge_text)

    # In a real RAG system, you would load documents from files (PDFs, docs).
    # Here, we treat the entire LLM_RAG_CONTEXT as one document.
    return vector, knowledge_text
