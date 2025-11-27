import os
import sys
import json
import wave
from vosk import Model, KaldiRecognizer

class VoskTranscriber:
    def __init__(self, model_path="models/vosk-model-small-en-us-0.15"):
        if not os.path.exists(model_path):
            print(f"Model not found at {model_path}")
            print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'models/vosk-model-small-en-us-0.15'")
            sys.exit(1)
        self.model = Model(model_path)

    def transcribe(self, audio_bytes):
        # Create a recognizer for each transcription to ensure clean state
        rec = KaldiRecognizer(self.model, 16000)
        rec.AcceptWaveform(audio_bytes)
        result = rec.FinalResult()
        text = json.loads(result)["text"]
        return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_vosk.py <path_to_wav>")
        sys.exit(1)

    wav_path = sys.argv[1]
    if not os.path.exists(wav_path):
        print(f"File not found: {wav_path}")
        sys.exit(1)

    try:
        wf = wave.open(wav_path, "rb")
    except wave.Error as e:
        print(f"Could not open wav file: {e}")
        sys.exit(1)

    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

    if wf.getframerate() != 16000:
        print("Audio file must be 16kHz.")
        sys.exit(1)

    transcriber = VoskTranscriber()
    
    data = wf.readframes(wf.getnframes())
    wf.close()

    text = transcriber.transcribe(data)
    print(f"Transcription: {text}")
