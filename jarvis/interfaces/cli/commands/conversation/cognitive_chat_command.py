from jarvis.interfaces.cli.commands.base_command import BaseCommand
from jarvis.infrastructure.memory.vector_store import VectorMemory
from jarvis.infrastructure.voice.voice_engine import VoiceEngine
import json
import logging

class CognitiveChatCommand(BaseCommand):
    """Agente principal com Memória de Longo Prazo e Voz Global."""

    def __init__(self, llm_client, conversation_service, system_health, system_controller, workspace_manager):
        self.llm_client = llm_client
        self.conversation_service = conversation_service
        self.system_health = system_health
        self.system_controller = system_controller
        self.workspace_manager = workspace_manager
        

        self.memoria = VectorMemory()
        self.voice = VoiceEngine()
        
        self.arsenal = [
            {"type": "function", "function": {"name": "get_system_health", "description": "Verifica os sinais vitais do hardware."}},
            {"type": "function", "function": {"name": "open_application", "description": "Abre um app.", "parameters": {"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]}}},
            {"type": "function", "function": {"name": "launch_workspace", "description": "ABRE um projeto.", "parameters": {"type": "object", "properties": {"workspace_name": {"type": "string"}}, "required": ["workspace_name"]}}},
            {"type": "function", "function": {"name": "close_workspace", "description": "FECHA um projeto.", "parameters": {"type": "object", "properties": {"workspace_name": {"type": "string"}}, "required": ["workspace_name"]}}},
            {"type": "function", "function": {"name": "recalibrate_workspace", "description": "Corrige o caminho de um projeto.", "parameters": {"type": "object", "properties": {"workspace_name": {"type": "string"}, "path_hint": {"type": "string"}}, "required": ["workspace_name"]}}}
        ]

    def _falar_e_retornar(self, texto: str) -> str:
        """Centralizador: envia para a Engine de Voz e retorna o texto para o console."""
        if texto and len(texto.strip()) > 0:
            self.voice.speak(texto)
        return texto

    def matches(self, text: str) -> bool:
        return True

    def execute(self, text: str, context: dict) -> str:
        user = context.get("user")
        
        contexto_vetorial = self.memoria.consultar(text)
        self.memoria.registrar(text)
        contexto_str = "\n".join(contexto_vetorial)
        
        system_prompt = (
            "Você é J.A.R.V.I.S., ecossistema cognitivo avançado. "
            f"Administrador: {user.name}. "
            f"Memória Relevante: {contexto_str}\n\n"
            "DIRETRIZES: Responda de forma concisa, técnica e elegante em português."
        )
        
        try:
            history = self.conversation_service.get_recent_context(limit=5)
            
            resposta_ia = self.llm_client.pensar(system_prompt, text, history, tools=self.arsenal)
            
            if resposta_ia["tipo"] == "texto":
                return self._falar_e_retornar(resposta_ia["dados"])
                
            elif resposta_ia["tipo"] == "acao":
                tool_calls = resposta_ia["dados"]
                updated_history = list(history)
                updated_history.append({"role": "user", "content": text})
                updated_history.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
                
                for chamada in tool_calls:
                    nome_funcao = chamada["function"]["name"]
                    call_id = chamada.get("id")
                    argumentos = json.loads(chamada["function"].get("arguments", "{}"))
                    
                    try:
                        if nome_funcao == "launch_workspace":
                            msg = self.workspace_manager.launch_workspace(argumentos.get("workspace_name"))
                        elif nome_funcao == "close_workspace":
                            msg = self.workspace_manager.close_workspace(argumentos.get("workspace_name"))
                        elif nome_funcao == "recalibrate_workspace":
                            msg = self.workspace_manager.recalibrate_workspace(argumentos.get("workspace_name"), argumentos.get("path_hint"))
                        elif nome_funcao == "get_system_health":
                            msg = json.dumps(self.system_health.get_system_health())
                        elif nome_funcao == "open_application":
                            msg = f"Iniciando {argumentos.get('app_name')}..."
                            self.system_controller.open_application(argumentos.get("app_name"))
                        else:
                            msg = "Função não encontrada."
                            
                        resultado_ferramenta = {"status": "sucesso", "mensagem": msg}
                    except Exception as func_err:
                        resultado_ferramenta = {"status": "erro", "mensagem": str(func_err)}
                        
                    updated_history.append({"role": "tool", "tool_call_id": call_id, "name": nome_funcao, "content": json.dumps(resultado_ferramenta)})
                
                resposta_final = self.llm_client.pensar(system_prompt, "Explain the action result to the user", updated_history, tools=None)
                return self._falar_e_retornar(resposta_final["dados"])
                
        except Exception as e:
            return self._falar_e_retornar(f"Erro no link neural: {e}")