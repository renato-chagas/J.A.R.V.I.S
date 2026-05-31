import subprocess
import edge_tts
import threading

class VoiceEngine:
    def __init__(self, voice="pt-BR-FranciscaNeural"):
        self.voice = voice

    def speak(self, text: str):
        thread = threading.Thread(target=self._process_audio, args=(text,))
        thread.start()

    def _process_audio(self, text):
        output_file = "/tmp/jarvis_out.mp3"
        cmd = f"edge-tts --text '{text}' --write-media {output_file} --voice {self.voice}"
        subprocess.run(cmd, shell=True, capture_output=True)
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", output_file], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)