import whisper

class Listener:
    def __init__(self):
        self.model = whisper.load_model("tiny")

    def ouvir(self):
        os.system("arecord -d 3 -f cd /tmp/audio.wav")
        resultado = self.model.transcribe("/tmp/audio.wav")
        return resultado["text"]