import sys
import os
import whisper
import numpy as np
import wave

class WhisperTranscriber:
    def __init__(self, model_name="base"):
        print(f"Loading Whisper model: {model_name}...")
        self.model = whisper.load_model(model_name)
        print("Model loaded.")

    def transcribe(self, audio_data, language="en"):
        """
        Transcribe audio data.
        audio_data: can be a file path or numpy array of audio samples.
        If passing bytes, they need to be converted to float32 numpy array normalized to [-1, 1].
        """
        # Whisper expects a float32 numpy array or a path
        # If audio_data is bytes (from wave readframes), we need to convert it.
        
        if isinstance(audio_data, bytes):
             # Assuming 16kHz, 16-bit mono based on previous context
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            result = self.model.transcribe(audio_np, language=language)
        else:
            # Let whisper handle file paths or already processed numpy arrays
            result = self.model.transcribe(audio_data, language=language)
            
        return result["text"].strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_whisper.py <path_to_wav>")
        sys.exit(1)

    wav_path = sys.argv[1]
    if not os.path.exists(wav_path):
        print(f"File not found: {wav_path}")
        sys.exit(1)

    transcriber = WhisperTranscriber()
    
    # Whisper can read the file directly, which is often better as it handles resampling if needed
    text = transcriber.transcribe(wav_path)
    print(f"Transcription: {text}")
