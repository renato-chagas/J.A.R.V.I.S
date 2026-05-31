import chromadb
from sentence_transformers import SentenceTransformer
import os

class VectorMemory:
    def __init__(self):
        os.makedirs("data/db/memory_vectors", exist_ok=True)
        self.client = chromadb.PersistentClient(path="data/db/memory_vectors")
        self.collection = self.client.get_or_create_collection("conversa_do_tulipa")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def registrar(self, texto: str):
        """Store a new piece of knowledge."""
        if not texto.strip(): return
        embedding = self.model.encode(texto).tolist()
        doc_id = str(hash(texto))
        self.collection.upsert(ids=[doc_id], embeddings=[embedding], documents=[texto])

    def consultar(self, pergunta: str, limite=3):
        """Retrieve the most relevant conversation pieces."""
        embedding = self.model.encode(pergunta).tolist()
        resultados = self.collection.query(query_embeddings=[embedding], n_results=limite)
        return resultados['documents'][0] if resultados['documents'] else []