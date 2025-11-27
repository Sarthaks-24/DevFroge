import os
import pytest
import time
import csv
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transcribe_whisper import WhisperTranscriber
from utils_clean import clean_text

# Fixture to initialize the transcriber once
@pytest.fixture(scope="session")
def transcriber():
    print("\nInitializing Whisper Model for tests...")
    return WhisperTranscriber(model_name="base")

# Define test cases: (filename, expected_snippet, description)
# You should place these files in tests/fixtures/ or adjust paths
TEST_CASES = [
    # (path, expected_text_part, description)
    # Using existing recordings as placeholders since I don't have specific fixtures yet
    ("recordings/chunk_20251127_124720_634937.wav", "camera", "Short clear speech"),
    # Add more test files here
]

@pytest.fixture(scope="session")
def metrics_file():
    filename = "test_metrics.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Filename', 'Description', 'Transcription_Time', 'Cleaning_Time', 'Total_Time', 'Original_Length', 'Cleaned_Length', 'Grammar_Check'])
    return filename

@pytest.mark.parametrize("audio_path, expected_snippet, description", TEST_CASES)
def test_pipeline_metrics(transcriber, metrics_file, audio_path, expected_snippet, description):
    """
    Runs the full pipeline on an audio file and logs metrics.
    """
    full_path = os.path.abspath(audio_path)
    if not os.path.exists(full_path):
        pytest.skip(f"Audio file not found: {full_path}")

    # 1. Transcribe
    start_transcribe = time.time()
    original_text = transcriber.transcribe(full_path)
    transcribe_time = time.time() - start_transcribe

    # 2. Clean (without grammar)
    start_clean = time.time()
    cleaned_text = clean_text(original_text, use_grammar_tool=False)
    clean_time = time.time() - start_clean

    # Log metrics
    with open(metrics_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            os.path.basename(audio_path),
            description,
            f"{transcribe_time:.4f}",
            f"{clean_time:.4f}",
            f"{transcribe_time + clean_time:.4f}",
            len(original_text),
            len(cleaned_text),
            False
        ])

    # Assertions
    assert expected_snippet.lower() in original_text.lower(), f"Expected '{expected_snippet}' in transcription"
    assert len(cleaned_text) > 0, "Cleaned text should not be empty"

@pytest.mark.parametrize("audio_path, expected_snippet, description", TEST_CASES)
def test_pipeline_metrics_with_grammar(transcriber, metrics_file, audio_path, expected_snippet, description):
    """
    Runs the full pipeline WITH grammar correction and logs metrics.
    """
    full_path = os.path.abspath(audio_path)
    if not os.path.exists(full_path):
        pytest.skip(f"Audio file not found: {full_path}")

    # 1. Transcribe
    start_transcribe = time.time()
    original_text = transcriber.transcribe(full_path)
    transcribe_time = time.time() - start_transcribe

    # 2. Clean (WITH grammar)
    start_clean = time.time()
    cleaned_text = clean_text(original_text, use_grammar_tool=True)
    clean_time = time.time() - start_clean

    # Log metrics
    with open(metrics_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            os.path.basename(audio_path),
            description,
            f"{transcribe_time:.4f}",
            f"{clean_time:.4f}",
            f"{transcribe_time + clean_time:.4f}",
            len(original_text),
            len(cleaned_text),
            True
        ])

    # Assertions
    assert expected_snippet.lower() in original_text.lower()
