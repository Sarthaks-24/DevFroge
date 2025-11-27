import os
import time
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from transcribe_whisper import WhisperTranscriber
from utils_clean import clean_text

app = Flask(__name__, static_url_path='')

# Initialize Transcriber (Global to avoid reloading model)
# Using Whisper as per previous instructions to replace Vosk
print("Initializing Whisper Model...")
transcriber = WhisperTranscriber(model_name="base")
print("Whisper Model Initialized.")

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Options
    use_grammar = request.form.get('grammar', 'false').lower() == 'true'
    language = request.form.get('language', 'en')

    timings = {}
    
    # 1. Transcription
    start_transcribe = time.time()
    
    # Save to temp file to let Whisper handle file format/headers correctly
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        file.save(temp_wav)
        temp_wav_path = temp_wav.name
        
    try:
        raw_text = transcriber.transcribe(temp_wav_path, language=language)
    except Exception as e:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
    
    # Cleanup temp file
    if os.path.exists(temp_wav_path):
        os.remove(temp_wav_path)
        
    timings['transcription'] = time.time() - start_transcribe

    # 2. Cleaning (includes optional grammar correction)
    start_clean = time.time()
    cleaned_text = clean_text(raw_text, use_grammar_tool=use_grammar)
    timings['cleaning'] = time.time() - start_clean
    
    timings['total'] = timings['transcription'] + timings['cleaning']

    response_data = {
        "original_text": raw_text,
        "cleaned_text": cleaned_text,
        "timings": timings
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
