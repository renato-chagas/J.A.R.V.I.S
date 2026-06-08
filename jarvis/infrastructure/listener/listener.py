import whisper
import os
import logging
import speech_recognition as sr

class AudioListener:
    """Captação de áudio dinâmica com Voice Activity Detection (VAD) via silêncio."""

    def __init__(self):
        logging.info("[Audição] Carregando modelo Whisper (tiny)...")
        self.model = whisper.load_model("tiny")
        self.temp_audio = "/tmp/jarvis_input.wav"
        
        # Inicializa o reconhecedor que vai gerenciar o silêncio
        self.recognizer = sr.Recognizer()
        
        # Ajustes de sensibilidade para silêncio
        self.recognizer.pause_threshold = 1.0 # Tempo de silêncio (em segundos) para considerar que você parou de falar
        self.recognizer.energy_threshold = 300 # Nível de volume base (se ajusta dinamicamente)

    def ouvir(self) -> str:
        """Escuta o microfone de forma contínua até detectar silêncio e transcreve."""
        print("\n--- [Microfone Aberto] Pode falar... ---")
        
        # O sr.Microphone vai achar o seu headset automaticamente na maioria dos casos no Linux
        with sr.Microphone() as source:
            # Calibra rapidamente o ruído de fundo do ambiente
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Ouve até você parar de falar. 
                # timeout=5: Desiste se você não falar nada em 5 segundos
                # phrase_time_limit=15: Corta se você falar sem parar por 15 segundos (evita travar)
                audio_data = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                
                print("--- [Processando Áudio] ---")
                
                # Salva os bytes captados em um arquivo WAV temporário
                with open(self.temp_audio, "wb") as f:
                    f.write(audio_data.get_wav_data())
                
                # Passa o WAV dinâmico para o Whisper transcrever
                result = self.model.transcribe(self.temp_audio, language="pt")
                texto = result["text"].strip()
                
                print(f"--- Você disse: {texto} ---")
                return texto
                
            except sr.WaitTimeoutError:
                print("--- [Timeout] Nenhum som detectado. ---")
                return ""
            except Exception as e:
                logging.error(f"[Audição] Falha ao captar ou processar áudio: {e}")
                return ""