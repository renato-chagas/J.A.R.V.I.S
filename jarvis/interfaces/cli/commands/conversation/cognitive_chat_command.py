from jarvis.interfaces.cli.commands.base_command import BaseCommand
from jarvis.infrastructure.memory.vector_store import VectorMemory
from jarvis.infrastructure.voice.voice_engine import VoiceEngine
import json
import logging


class CognitiveChatCommand(BaseCommand):
    """Agente principal com Memória de Longo Prazo e Voz Global."""

    def __init__(
        self,
        llm_client,
        conversation_service,
        system_health,
        system_controller,
        workspace_manager,
        screen_reader,
    ):
        self.llm_client = llm_client
        self.conversation_service = conversation_service
        self.system_health = system_health
        self.system_controller = system_controller
        self.workspace_manager = workspace_manager
        self.screen_reader = screen_reader

        self.memoria = VectorMemory()
        self.voice = VoiceEngine()

        self.arsenal = [
            {
                "type": "function",
                "function": {
                    "name": "get_system_health",
                    "description": "Verifica os sinais vitais do hardware (CPU, RAM, Disco). Use APENAS se o usuário perguntar especificamente sobre uso de CPU, RAM, disco ou a saúde do sistema.",
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Abre um aplicativo no sistema operacional.",
                    "parameters": {
                        "type": "object",
                        "properties": {"app_name": {"type": "string"}},
                        "required": ["app_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "launch_workspace",
                    "description": "Abre um projeto ou ambiente de trabalho.",
                    "parameters": {
                        "type": "object",
                        "properties": {"workspace_name": {"type": "string"}},
                        "required": ["workspace_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "close_workspace",
                    "description": "Fecha um projeto ou ambiente de trabalho.",
                    "parameters": {
                        "type": "object",
                        "properties": {"workspace_name": {"type": "string"}},
                        "required": ["workspace_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "recalibrate_workspace",
                    "description": "Corrige o caminho de um projeto.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "workspace_name": {"type": "string"},
                            "path_hint": {"type": "string"},
                        },
                        "required": ["workspace_name"],
                    },
                },
            },
            {
                "type": "function", 
                "function": {
                    "name": "screen_reader", 
                    "description": "Tira um print da tela para analisar o que está acontecendo no seu ambiente de trabalho."
                }
            }
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
            "Você é J.A.R.V.I.S., um ecossistema cognitivo avançado. "
            f"Administrador: {user.name}. "
            f"MEMÓRIA DE LONGO PRAZO: {contexto_str}"
            "DIRETRIZES: "
            "1. AGISMO: Você é proativo. Se eu pedir algo, você executa o comando técnico imediatamente antes de explicar. "
            "2. PERSONALIDADE: Você é direto, técnico e confiante. Evite perguntas como 'Gostaria que eu fizesse?'. Se o comando é claro, a ação é imediata. Haja como o jarvis do homem de ferro "
            "3. LINGUAGEM: Use termos como 'Protocolo iniciado', 'Status operacional', 'Ação concluída'."
        )

        try:
            history = self.conversation_service.get_recent_context(limit=5)
            resposta_ia = self.llm_client.pensar(
                system_prompt,
                text,
                historico=history,
                tools=self.arsenal,
            )

            if not resposta_ia or "tipo" not in resposta_ia:
                return self._falar_e_retornar("Falha na comunicação com o motor cognitivo.")

            if resposta_ia["tipo"] == "texto":
                return self._falar_e_retornar(resposta_ia.get("dados", "Processo concluído."))

            elif resposta_ia["tipo"] == "acao":
                tool_calls = resposta_ia["dados"]
                updated_history = list(history)
                updated_history.append({"role": "user", "content": text})
                updated_history.append({"role": "assistant", "content": None, "tool_calls": tool_calls})

                for chamada in tool_calls:
                    nome_funcao = chamada["function"]["name"]
                    call_id = chamada.get("id", "call_default_id")
                    argumentos = json.loads(chamada["function"].get("arguments", "{}"))

                    try:
                        if nome_funcao == "launch_workspace":
                            msg = self.workspace_manager.launch_workspace(argumentos.get("workspace_name"))
                        elif nome_funcao == "close_workspace":
                            msg = self.workspace_manager.close_workspace(argumentos.get("workspace_name"))
                        elif nome_funcao == "screen_reader":
                            logging.info("Executando ferramenta: screen_reader")
                            # Usar OCR local para extrair texto e evitar enviar imagem para o LLM
                            try:
                                texto_tela = self.screen_reader.capturar_e_ler()
                                # Se não houver texto no monitor 2, tente o desktop completo como fallback
                                if not texto_tela or len(texto_tela.strip()) == 0:
                                    logging.info("Nenhum texto no monitor 2 — tentando desktop completo.")
                                    texto_tela = self.screen_reader.capturar_full_e_ler()

                                if texto_tela and len(texto_tela.strip()) > 0:
                                    # Limitar tamanho exibido para evitar mensagens gigantes
                                    resumo = texto_tela.strip()
                                    if len(resumo) > 1500:
                                        resumo = resumo[:1500] + "..."
                                    logging.info("Texto extraído com sucesso da tela.")
                                    msg = f"Conteúdo extraído da tela: {resumo}"
                                else:
                                    logging.info("Nenhum texto detectado após OCR.")
                                    msg = "Nenhum texto detectado na tela (tente instalar tesseract/pytesseract se necessário)."
                            except Exception as _ocr_err:
                                logging.error(f"Erro OCR: {_ocr_err}")
                                msg = f"Falha na leitura da tela: {_ocr_err}"
                        elif nome_funcao == "open_application":
                            app = argumentos.get('app_name')
                            self.system_controller.open_application(app)
                            msg = f"Aplicativo {app} executado."
                        else:
                            msg = "Função não mapeada."
                        resultado_ferramenta = {"status": "sucesso", "mensagem": msg}
                    except Exception as e:
                        resultado_ferramenta = {"status": "erro", "mensagem": str(e)}

                    updated_history.append({"role": "tool", "tool_call_id": call_id, "name": nome_funcao, "content": json.dumps(resultado_ferramenta)})

                resposta_final = self.llm_client.pensar(
                    system_prompt,
                    "Resuma a ação realizada.",
                    historico=updated_history,
                    tools=None,
                )
                return self._falar_e_retornar(resposta_final.get("dados", "Ação concluída."))

        except Exception as e:
            logging.error(f"Erro crítico no sistema: {e}")
            return self._falar_e_retornar(f"Falha técnica: {str(e)}")
        
        return self._falar_e_retornar("Protocolo concluído.")