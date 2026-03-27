from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Load model once at module level (lazy loading)
_model = None

def _get_model():
    global _model
    if _model is None:
        logger.info("Loading embedding model (first time only)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded")
    return _model

def get_embedding(text: str) -> list:
    """Convert text to a 384-dimensional embedding vector."""
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def cosine_similarity(vec1: list, vec2: list) -> float:
    """Compute cosine similarity between two vectors. Returns 0-1."""
    a = np.array(vec1)
    b = np.array(vec2)
    similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(max(0.0, similarity))
