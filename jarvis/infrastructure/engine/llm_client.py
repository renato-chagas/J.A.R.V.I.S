import requests
import json
import base64
import os

class LocalLLMClient:
    def __init__(self, host="http://localhost:8080"):
        self.url = f"{host}/v1/chat/completions"
        self.headers = {"Content-Type": "application/json"}

    def _encode_image(self, image_path):
        """Converte imagem local para Base64 para envio ao LLM."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _guess_image_mime(self, image_path: str) -> str:
        ext = os.path.splitext(image_path.lower())[1]
        if ext in {'.jpg', '.jpeg'}:
            return 'image/jpeg'
        if ext == '.webp':
            return 'image/webp'
        return 'image/png'

    def pensar(self, instrucao_sistema, mensagem_usuario, imagem_path=None, historico=None, tools=None, temperature=0.7):
        historico = historico or []
        mensagens = [{"role": "system", "content": instrucao_sistema}]
        mensagens.extend(historico)
        
        # Estrutura de conteúdo multimodal
        content = [{"type": "text", "text": str(mensagem_usuario)}]
        
        if imagem_path:
            img_b64 = self._encode_image(imagem_path)
            mime = self._guess_image_mime(imagem_path)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{img_b64}"}
            })
            
        mensagens.append({"role": "user", "content": content})

        payload = {"messages": mensagens, "temperature": temperature}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            resposta = requests.post(self.url, headers=self.headers, json=payload)
            resposta.raise_for_status()
            dados = resposta.json()
            mensagem_resposta = dados['choices'][0]['message']

            if "tool_calls" in mensagem_resposta and mensagem_resposta["tool_calls"]:
                return {"tipo": "acao", "dados": mensagem_resposta["tool_calls"]}

            return {"tipo": "texto", "dados": mensagem_resposta.get('content', '')}

        except requests.exceptions.HTTPError as e:
            detalhe = ""
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    detalhe = resp.text
                except Exception:
                    detalhe = str(resp)
            return {"tipo": "erro", "dados": f"[Erro no Link Neural]: {e}. {detalhe}".strip()}
        except Exception as e:
            return {"tipo": "erro", "dados": f"[Erro no Link Neural]: {e}"}
        
