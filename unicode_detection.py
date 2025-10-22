"""
Unicode obfuscation and evasion detection
Catches homoglyphs, zero-width chars, RTL overrides, and other tricks
"""
import re
import unicodedata
from typing import List, Tuple


def detect_unicode_tricks(text: str) -> Tuple[float, List[str]]:
    """
    Detect Unicode-based obfuscation and evasion attempts.
    
    Returns:
        tuple: (risk_score, list_of_reasons)
    """
    flags = []
    score = 0.0
    
    # 1. Bidirectional text override (RTL tricks)
    if "\u202e" in text:  # RIGHT-TO-LEFT OVERRIDE
        flags.append("RTL override detected")
        score += 0.4
    if "\u2066" in text or "\u2067" in text or "\u2068" in text:  # Directional isolates
        flags.append("Bidirectional embedding")
        score += 0.3
    
    # 2. Zero-width characters (invisible chars for hiding)
    zero_width_pattern = r'[\u200B-\u200F\u2060\uFEFF]'
    zero_width_matches = re.findall(zero_width_pattern, text)
    if zero_width_matches:
        flags.append(f"Zero-width chars detected ({len(zero_width_matches)})")
        score += min(0.5, len(zero_width_matches) * 0.1)
    
    # 3. Fullwidth/halfwidth lookalikes (homoglyphs)
    fullwidth_pattern = r'[Ａ-Ｚａ-ｚ０-９]'
    if re.search(fullwidth_pattern, text):
        flags.append("Fullwidth character lookalikes")
        score += 0.3
    
    # 4. Cyrillic/Greek lookalikes (common in phishing)
    # Latin 'a' vs Cyrillic 'а', Latin 'e' vs Cyrillic 'е'
    cyrillic_lookalikes = ['а', 'е', 'о', 'р', 'с', 'у', 'х', 'А', 'В', 'С', 'Е', 'Н', 'К', 'М', 'О', 'Р', 'Т', 'Х']
    for char in cyrillic_lookalikes:
        if char in text and any(c.isalpha() and ord(c) < 128 for c in text):
            flags.append("Cyrillic/Latin homoglyphs detected")
            score += 0.4
            break
    
    # 5. Combining characters (stacking diacritics)
    combining_chars = [c for c in text if unicodedata.category(c) == 'Mn']
    if len(combining_chars) > len(text) * 0.1:  # >10% combining chars is suspicious
        flags.append(f"Excessive combining characters ({len(combining_chars)})")
        score += 0.3
    
    # 6. Control characters (non-printable)
    control_chars = [c for c in text if unicodedata.category(c) == 'Cc' and c not in '\n\r\t']
    if control_chars:
        flags.append(f"Control characters detected ({len(control_chars)})")
        score += 0.3
    
    # 7. Mathematical Alphanumeric Symbols (𝓐𝓑𝓒, 𝕬𝕭𝕮)
    math_alpha_pattern = r'[\U0001D400-\U0001D7FF]'
    if re.search(math_alpha_pattern, text):
        flags.append("Mathematical alphanumeric symbols")
        score += 0.3
    
    # 8. Enclosed Alphanumerics (①②③, ⒶⒷⒸ)
    enclosed_pattern = r'[\u2460-\u24FF]'
    if re.search(enclosed_pattern, text):
        flags.append("Enclosed alphanumeric characters")
        score += 0.2
    
    # 9. Excessive Base64-like patterns (potential encoding obfuscation)
    base64_chunks = re.findall(r'[A-Za-z0-9+/]{50,}={0,2}', text)
    if len(base64_chunks) > 2:
        flags.append(f"Multiple Base64-like sequences ({len(base64_chunks)})")
        score += 0.3
    
    # 10. ROT13 or Caesar cipher patterns (repeated character shifts)
    # Simple heuristic: if text has unusual letter frequency distribution
    if len(text) > 50:
        letter_freq = {}
        for c in text.lower():
            if c.isalpha():
                letter_freq[c] = letter_freq.get(c, 0) + 1
        if letter_freq:
            # Check if distribution is very flat (characteristic of cipher)
            avg_freq = sum(letter_freq.values()) / len(letter_freq)
            variance = sum((f - avg_freq) ** 2 for f in letter_freq.values()) / len(letter_freq)
            if variance < avg_freq * 0.5:  # Low variance = suspicious
                flags.append("Unusual character distribution (possible cipher)")
                score += 0.2
    
    # 11. Mixed scripts (unusual combinations)
    scripts = set()
    for char in text:
        if char.isalpha():
            try:
                script = unicodedata.name(char).split()[0]
                scripts.add(script)
            except ValueError:
                pass
    
    suspicious_script_combos = [
        ('LATIN', 'CYRILLIC'),
        ('LATIN', 'GREEK'),
        ('ARABIC', 'LATIN'),
    ]
    
    for script1, script2 in suspicious_script_combos:
        if script1 in scripts and script2 in scripts:
            flags.append(f"Mixed scripts: {script1}/{script2}")
            score += 0.3
            break
    
    return min(1.0, score), flags


def find_pattern_spans(text: str, pattern: re.Pattern) -> List[Tuple[int, int]]:
    """
    Find character offsets for all matches of a compiled regex pattern.
    
    Args:
        text: Input text to search
        pattern: Compiled regex pattern
        
    Returns:
        list: [(start_offset, end_offset), ...]
    """
    return [(m.start(), m.end()) for m in pattern.finditer(text)]


def detect_compression_bomb(text: str, max_ratio: float = 100.0) -> Tuple[bool, str]:
    """
    Detect potential compression bombs (highly compressible malicious input).
    
    Args:
        text: Input text
        max_ratio: Maximum allowed compression ratio
        
    Returns:
        tuple: (is_bomb, reason)
    """
    import zlib
    
    if len(text) < 100:
        return False, ""
    
    try:
        compressed = zlib.compress(text.encode('utf-8'), level=9)
        ratio = len(text) / len(compressed)
        
        if ratio > max_ratio:
            return True, f"Compression ratio {ratio:.1f}:1 exceeds threshold"
    except Exception:
        pass
    
    return False, ""


def detect_homoglyphs(text: str, suspicious_threshold: int = 3) -> Tuple[bool, List[str]]:
    """
    Detect homoglyph attacks (visually similar but different Unicode chars).
    
    Args:
        text: Input text
        suspicious_threshold: Number of homoglyphs to trigger warning
        
    Returns:
        tuple: (is_suspicious, list_of_examples)
    """
    # Common homoglyph pairs (visually similar)
    homoglyph_pairs = {
        'a': ['а', 'ａ', 'ɑ'],  # Latin a vs Cyrillic/fullwidth/Greek
        'e': ['е', 'ｅ', 'е'],  # Latin e vs Cyrillic/fullwidth
        'o': ['о', 'ο', 'ｏ', '０'],  # Latin o vs Cyrillic/Greek/fullwidth
        'p': ['р', 'ρ', 'ｐ'],  # Latin p vs Cyrillic/Greek
        'c': ['с', 'ϲ', 'ｃ'],  # Latin c vs Cyrillic/Greek
        'i': ['і', 'ɪ', 'ｉ'],  # Latin i vs Cyrillic/other
        '0': ['О', 'о', 'Ο', 'ο'],  # Zero vs O
        '1': ['l', 'I', 'ǀ', 'Ӏ'],  # One vs L/I
    }
    
    found_homoglyphs = []
    for latin_char, lookalikes in homoglyph_pairs.items():
        if latin_char in text:
            for lookalike in lookalikes:
                if lookalike in text:
                    found_homoglyphs.append(f"'{latin_char}' mixed with '{lookalike}'")
    
    is_suspicious = len(found_homoglyphs) >= suspicious_threshold
    
    return is_suspicious, found_homoglyphs
