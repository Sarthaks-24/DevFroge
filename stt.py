import os
import sys
import shutil
import subprocess
import warnings
import whisper

# Suppress FP16 warning if running on CPU
warnings.filterwarnings("ignore", category=UserWarning)

def check_ffmpeg():
    """Check if FFmpeg is installed and available in PATH."""
    return shutil.which("ffmpeg") is not None

def convert_to_wav(input_path):
    """
    Converts audio to 16kHz mono WAV using FFmpeg.
    Returns the path to the converted file.
    """
    output_path = "temp_converted.wav"
    try:
        # -y overwrites output, -ar 16000 sets sample rate, -ac 1 sets mono
        command = [
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1",
            "-c:a", "pcm_s16le", output_path
        ]
        # Run silently
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except subprocess.CalledProcessError:
        print("Error: FFmpeg failed to convert the audio.")
        sys.exit(1)

def transcribe_audio(audio_path):
    """Loads the local Whisper model and transcribes the audio."""
    try:
        # 'base' is a good balance of speed/accuracy. Use 'tiny' for speed, 'medium' for accuracy.
        # fp16=False ensures it runs on CPU without errors if GPU is missing.
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path, fp16=False)
        return result["text"]
    except Exception as e:
        return f"Error during transcription: {e}"

if __name__ == "__main__":
    print("--- Offline Whisper Speech-to-Text ---")
    
    # 1. Get User Input
    input_file = input("Enter path to audio file: ").strip().strip('"').strip("'")
    
    if not os.path.exists(input_file):
        print(f"Error: File not found at {input_file}")
        sys.exit(1)

    ffmpeg_installed = check_ffmpeg()
    final_audio_path = input_file
    temp_file_created = False

    # 2. FFmpeg Logic Checks
    if not ffmpeg_installed:
        # If FFmpeg is missing, only allow WAV files
        if not input_file.lower().endswith(".wav"):
            print("\nError: FFmpeg is not installed.")
            print("Without FFmpeg, this script can only process pre-formatted .wav files.")
            print("Please install FFmpeg or provide a .wav file.")
            sys.exit(1)
        else:
            print("FFmpeg not found. Attempting to process raw WAV file...")
    else:
        # If FFmpeg is present, normalize audio
        print("FFmpeg detected. converting audio to 16kHz mono WAV...")
        final_audio_path = convert_to_wav(input_file)
        temp_file_created = True

    # 3. Transcribe
    print("Transcribing... (this may take a moment)")
    transcription = transcribe_audio(final_audio_path)

    # 4. Output
    print("\n--- Transcription Result ---")
    print(transcription.strip())
    print("----------------------------")

    # Cleanup temp file if we created one
    if temp_file_created and os.path.exists(final_audio_path):
        os.remove(final_audio_path)