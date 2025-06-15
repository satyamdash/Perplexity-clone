import faiss
import numpy as np

class FAISSStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, vectors, texts):
        self.index.add(np.array(vectors).astype("float32"))
        self.texts.extend(texts)

    def search(self, query_vector, top_k=5):
        D, I = self.index.search(np.array([query_vector]).astype("float32"), top_k)
        return [self.texts[i] for i in I[0] if i < len(self.texts)]

    def save(self, path):
        faiss.write_index(self.index, path)

    def load(self, path):
        self.index = faiss.read_index(path)
