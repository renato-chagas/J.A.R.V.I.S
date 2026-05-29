import requests
import json

class LocalLLMClient:
    def __init__(self, host="http://localhost:8080"):
        # Define o endereço da API do seu motor C++ local
        self.url = f"{host}/v1/chat/completions"
        self.headers = {"Content-Type": "application/json"}

    def pensar(self, instrucao_sistema, mensagem_usuario, temperature=0.7):
        """
        Envia os dados via HTTP puro para o llama.cpp e retorna a resposta do J.A.R.V.I.S.
        """
        payload = {
            "messages": [
                {"role": "system", "content": instrucao_sistema},
                {"role": "user", "content": mensagem_usuario}
            ],
            "temperature": temperature
        }

        try:
            # Faz o disparo HTTP POST puro
            resposta = requests.post(
                self.url, 
                headers=self.headers, 
                data=json.dumps(payload)
            )
            
            # Se a API der erro (ex: servidor desligado), isso aciona a exceção
            resposta.raise_for_status()
            
            # Navega no JSON de retorno para extrair apenas a string com a fala da IA
            dados = resposta.json()
            return dados['choices'][0]['message']['content']
            
        except requests.exceptions.ConnectionError:
            return "[Erro Crítico]: O motor cognitivo (C++) está offline. Verifique se o llama-server está rodando na porta 8080."
        except Exception as e:
            return f"[Erro Interno]: Falha na comunicação estrutural - {e}"

# --- Bloco de Teste ---
# Este bloco só executa se você rodar este arquivo diretamente no terminal.
# Se o arquivo for importado por outro script, este bloco é ignorado.
if __name__ == "__main__":
    # 1. Instancia o cliente HTTP
    cerebro = LocalLLMClient()
    
    # 2. Prepara as instruções
    prompt_sistema = "Você é o J.A.R.V.I.S., um assistente cognitivo de código aberto. Responda de forma extremamente técnica, objetiva e em português."
    pergunta = "Iniciando protocolo de integração. Você consegue me ouvir?"
    
    print("Enviando pacote HTTP para a porta 8080...\n")
    
    # 3. Dispara a requisição e aguarda a resposta
    resposta_ia = cerebro.pensar(prompt_sistema, pergunta)
    
    print("J.A.R.V.I.S.:", resposta_ia)