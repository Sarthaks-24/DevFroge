import requests
import sys
import os

def test_transcription(wav_path, use_grammar=False):
    url = 'http://127.0.0.1:5000/transcribe'
    
    if not os.path.exists(wav_path):
        print(f"File not found: {wav_path}")
        return

    print(f"Sending {wav_path} to {url} (Grammar: {use_grammar})...")
    
    with open(wav_path, 'rb') as f:
        files = {'file': f}
        data = {'grammar': 'true' if use_grammar else 'false'}
        
        try:
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("\n--- Success ---")
                print(f"Original: {result['original_text']}")
                print(f"Cleaned:  {result['cleaned_text']}")
                print("Timings:")
                for k, v in result['timings'].items():
                    print(f"  {k}: {v:.4f}s")
            else:
                print(f"\n--- Error {response.status_code} ---")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("\nCould not connect to server. Is app.py running?")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_app.py <path_to_wav> [grammar=false]")
        sys.exit(1)
        
    wav_file = sys.argv[1]
    grammar = False
    if len(sys.argv) > 2 and sys.argv[2].lower() == 'true':
        grammar = True
        
    test_transcription(wav_file, grammar)
