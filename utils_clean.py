import re
import time
import language_tool_python

# Global tool instance to avoid respawning overhead
_tool = None

def get_language_tool():
    global _tool
    if _tool is None:
        print("Initializing LanguageTool (this may take a moment)...")
        start_time = time.time()
        _tool = language_tool_python.LanguageTool('en-US')
        print(f"LanguageTool initialized in {time.time() - start_time:.2f}s")
    return _tool

def correct_grammar(text):
    """
    Corrects grammar using LanguageTool.
    Returns the corrected text and the time taken.
    """
    tool = get_language_tool()
    
    start_time = time.time()
    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    duration = time.time() - start_time
    
    return corrected_text, duration

def remove_fillers(text, fillers=None):
    """
    Removes common filler words from the text.
    """
    # Default list of fillers to remove if none provided
    if fillers is None:
        fillers = ["um", "uh", "ah", "er", "hmm"]
    
    # Pattern to match fillers as whole words
    # \b(um|uh|...)\b
    pattern = r'\b(' + '|'.join(re.escape(f) for f in fillers) + r')\b'
    
    # Remove fillers (case-insensitive)
    cleaned = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Clean up multiple spaces resulting from removal
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def remove_repetitions(text):
    """
    Removes consecutive duplicate words (e.g. "the the" -> "the").
    """
    # Matches a word boundary, a word, a space, and the same word again
    # \1 refers to the first captured group (the word)
    pattern = r'\b(\w+)(?:\s+\1\b)+'
    
    # Function to replace with the first occurrence (preserving case of first word)
    def replace(match):
        return match.group(1)
        
    return re.sub(pattern, replace, text, flags=re.IGNORECASE)

def simple_punctuation(text, end_chars='.!?'):
    """
    Capitalizes the first letter and ensures the text ends with punctuation.
    """
    if not text:
        return text
    
    text = text.strip()
    
    # Capitalize first letter
    # text.capitalize() lowers the rest, so we do manual slicing
    first_char = text[0].upper()
    rest = text[1:]
    text = first_char + rest
    
    # Ensure end punctuation
    if text[-1] not in end_chars:
        text += end_chars[0]
        
    return text

def clean_text(text, fillers=None, use_grammar_tool=False):
    """
    Applies all cleaning functions to the text.
    """
    # Remove fillers first
    text = remove_fillers(text, fillers=fillers)
    
    # Remove repetitions (handles cases like "I um I" -> "I I" -> "I")
    text = remove_repetitions(text)
    
    # Apply punctuation
    text = simple_punctuation(text)
    
    if use_grammar_tool:
        text, duration = correct_grammar(text)
        # We could log duration here if needed
        
    return text

if __name__ == "__main__":
    print("Running tests for utils_clean.py...")
    
    test_cases = [
        "um hello world",
        "this is is a test",
        "I uh I think that er we should go",
        "no punctuation here",
        "Already punctuated!",
        "the the the end",
        "Testing testing 1 2 3"
    ]
    
    for input_text in test_cases:
        result = clean_text(input_text)
        print(f"Input:    '{input_text}'")
        print(f"Result:   '{result}'")
        print("-" * 20)

    # Test custom fillers
    print("Testing custom fillers (removing 'like'):")
    custom_input = "I like totally like this."
    custom_result = clean_text(custom_input, fillers=["like", "totally"])
    print(f"Input:    '{custom_input}'")
    print(f"Result:   '{custom_result}'")

    # Test grammar correction
    print("-" * 20)
    print("Testing grammar correction:")
    grammar_input = "I has a apple."
    print(f"Input:    '{grammar_input}'")
    grammar_result = clean_text(grammar_input, use_grammar_tool=True)
    print(f"Result:   '{grammar_result}'")
