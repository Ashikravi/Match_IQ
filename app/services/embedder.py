from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once at module level — not inside the function
# Loading a model takes ~2 seconds, you don't want that per request
model = SentenceTransformer('all-MiniLM-L6-v2')


def get_embedding(text: str) -> np.ndarray:
    """
    Converts text into a 384-dimensional vector.
    This vector captures the semantic meaning of the text.
    """
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding


def get_embeddings_batch(texts: list[str]) -> np.ndarray:
    """
    More efficient than calling get_embedding() in a loop.
    Processes multiple texts in one pass through the model.
    """
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings