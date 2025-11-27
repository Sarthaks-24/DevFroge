## Plan: Create `capture_vad.py` for Audio Capture and VAD

I will create a Python script that captures audio from the microphone, uses WebRTC VAD to detect voice activity, and groups the audio into speech segments (chunks). I will also create a requirements file for the necessary dependencies.

### Steps
1. Create `requirements.txt` listing `pyaudio` and `webrtcvad`.
2. Create `capture_vad.py` with the following components:
    - **Audio Configuration**: Set up PyAudio for 16kHz, mono, 16-bit PCM (required by WebRTC VAD).
    - **Frame Generator**: A helper to yield audio frames of 30ms duration.
    - **VAD Collector**: A generator function using a ring buffer to smooth detection (handling start/end padding) and yield complete speech chunks.
    - **Main Loop**: Captures audio, feeds the collector, and writes detected speech chunks to timestamped PCM/WAV files.

### Further Considerations
1. **Output Format**: Do you prefer raw PCM files or WAV files (with headers) for the output chunks? (I will default to WAV for easier playback).
2. **Dependencies**: You will need to install the requirements (`pip install -r requirements.txt`) and ensure you have a working microphone.
3. **Vosk Integration**: Since you have a Vosk model, this script can be easily modified later to yield bytes directly to a recognizer instead of writing files.
