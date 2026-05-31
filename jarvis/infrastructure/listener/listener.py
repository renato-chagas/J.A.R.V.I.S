import whisper
import os
import logging

class AudioListener:
    def __init__(self):
        self.model = whisper.load_model("tiny")
        self.temp_audio = "/tmp/jarvis_input.wav"
        self.device = "hw:0,0"

    def ouvir(self):
        """Record audio from Redragon Headset and transcribe."""
        print("\n--- Listening... ---")
        
        cmd = f"arecord -D {self.device} -d 4 -f S16_LE -r 16000 -c 1 {self.temp_audio} -q"
        
        if os.system(cmd) != 0:
            return "Error: Could not access the microphone."
        
        result = self.model.transcribe(self.temp_audio, language="pt")
        texto = result["text"].strip()
        
        print(f"--- You said: {texto} ---")
        return texto