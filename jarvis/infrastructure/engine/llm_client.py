import requests
import json

class LocalLLMClient:
    def __init__(self, host="http://localhost:8080"):
        self.url = f"{host}/v1/chat/completions"
        self.headers = {"Content-Type": "application/json"}

    def pensar(self, instrucao_sistema, mensagem_usuario, historico=None, tools=None, temperature=0.7):
        """
        Sends data via raw HTTP to llama.cpp, handling conversational memory and tool calls (Function Calling).
        """
        historico = historico or []
        mensagens = [{"role": "system", "content": instrucao_sistema}]
        mensagens.extend(historico)
        
        if isinstance(mensagem_usuario, dict):
            mensagens.append(mensagem_usuario)
        else:
            mensagens.append({"role": "user", "content": str(mensagem_usuario)})

        payload = {
            "messages": mensagens,
            "temperature": temperature
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto" # Permite que a IA decida se usa ou não

        try:
            resposta = requests.post(
                self.url, 
                headers=self.headers, 
                data=json.dumps(payload)
            )
            resposta.raise_for_status()
            
            dados = resposta.json()
            mensagem_resposta = dados['choices'][0]['message']
            
            if "tool_calls" in mensagem_resposta and mensagem_resposta["tool_calls"]:
                return {"tipo": "acao", "dados": mensagem_resposta["tool_calls"]}
            
            return {"tipo": "texto", "dados": mensagem_resposta.get('content', '')}
            
        except Exception as e:
            return {"tipo": "erro", "dados": f"[Erro no Link Neural]: {e}"}

# --- Test Block ---
# This block only runs when this file is executed directly in the terminal.
# If the file is imported by another script, this block is ignored.
if __name__ == "__main__":
    client = LocalLLMClient()
    
    system_prompt = "Você é o J.A.R.V.I.S., um assistente cognitivo de código aberto. Responda de forma extremamente técnica, objetiva e em português."
    question = "Iniciando protocolo de integração. Você consegue me ouvir?"
    
    print("Sending HTTP payload to port 8080...\n")
    
    response = client.pensar(system_prompt, question)
    
    print("J.A.R.V.I.S.:", response)