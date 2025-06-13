from typing import List, Dict
from sentence_transformers import SentenceTransformer

from app.core.settings import get_settings
settings = get_settings()

class TextEmbed:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for given text"""
        embedding = self.model.encode(text)
        return embedding.tolist()
    