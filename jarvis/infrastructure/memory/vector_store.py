import chromadb
from sentence_transformers import SentenceTransformer
import os
import hashlib
from datetime import datetime
import logging

class VectorMemory:
    """Gerencia a memória semântica de longo prazo do J.A.R.V.I.S."""

    def __init__(self):
        # 1. Caminho absoluto à prova de falhas
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(base_dir, "../../../data/db/memory_vectors"))
        os.makedirs(db_path, exist_ok=True)
        
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            # Definindo a métrica de distância como Cosine (ideal para NLP)
            self.collection = self.client.get_or_create_collection(
                name="conversa_do_tulipa",
                metadata={"hnsw:space": "cosine"} 
            )
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logging.info("[Hipocampo] Conexão com banco vetorial estabelecida.")
        except Exception as e:
            logging.error(f"[Hipocampo] Erro crítico ao carregar memória: {e}")
            self.client = None

    def registrar(self, texto: str):
        """Armazena um novo conhecimento com carimbo de tempo e ID consistente."""
        if not self.client or not texto.strip(): 
            return

        try:
            # 2. Hash determinístico: o mesmo texto sempre gerará o mesmo ID
            doc_id = hashlib.md5(texto.encode('utf-8')).hexdigest()
            
            # 3. Metadados para noção temporal
            timestamp_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            embedding = self.model.encode(texto).tolist()
            
            self.collection.upsert(
                ids=[doc_id], 
                embeddings=[embedding], 
                documents=[texto],
                metadatas=[{"data_hora": timestamp_atual}]
            )
        except Exception as e:
            logging.error(f"[Hipocampo] Erro ao gravar vetor: {e}")

    def consultar(self, pergunta: str, limite: int = 3):
        """Recupera as lembranças mais relevantes da conversa."""
        if not self.client or not pergunta.strip(): 
            return []

        try:
            embedding = self.model.encode(pergunta).tolist()
            
            resultados = self.collection.query(
                query_embeddings=[embedding], 
                n_results=limite
            )
            
            # Retorna a lista de textos encontrados, se houver
            if resultados and resultados.get('documents') and resultados['documents'][0]:
                # Opcional: Você pode formatar para devolver a data junto com a memória aqui
                memorias = resultados['documents'][0]
                return memorias
            return []
            
        except Exception as e:
            logging.error(f"[Hipocampo] Erro ao consultar vetores: {e}")
            return []