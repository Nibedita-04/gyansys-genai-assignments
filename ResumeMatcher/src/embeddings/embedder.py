from sentence_transformers import SentenceTransformer, util

class Embedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts, normalize=True):
        """
        Embed a list of texts into vectors.
        Returns a tensor or numpy array depending on your pipeline.
        """
        embeddings = self.model.encode(
            texts,
        )

        return embeddings