#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tamil Phonemic Converter
Decomposes consonant+vowel combinations into constituent phonemes

This module converts Tamil words from their written graphemic form to phonemic form
by decomposing all consonant+vowel combinations into their constituent parts:
consonant with pulli (்) + independent vowel letter.

Examples:
    ஒல்லென → ஒல்ல்என (where லெ → ல் + எ)
    அறம் → அறம் (no change, already in base form)
    கால் → க்ஆல் (கா → க் + ஆ)
"""

# Vowel sign to independent vowel mapping
# Maps combining vowel signs to their independent vowel letter equivalents
VOWEL_SIGN_TO_VOWEL = {
    'ா': 'ஆ',  # U+0BBE → U+0B86 (aa)
    'ி': 'இ',  # U+0BBF → U+0B87 (i)
    'ீ': 'ஈ',  # U+0BC0 → U+0B88 (ii)
    'ு': 'உ',  # U+0BC1 → U+0B89 (u)
    'ூ': 'ஊ',  # U+0BC2 → U+0B8A (uu)
    'ெ': 'எ',  # U+0BC6 → U+0B8E (e)
    'ே': 'ஏ',  # U+0BC7 → U+0B8F (ee)
    'ை': 'ஐ',  # U+0BC8 → U+0B90 (ai)
    'ொ': 'ஒ',  # U+0BCA → U+0B92 (o) - compound: ெ + ா
    'ோ': 'ஓ',  # U+0BCB → U+0B93 (oo) - compound: ே + ா
    'ௌ': 'ஔ',  # U+0BCC → U+0B94 (au) - compound: ெ + ௗ
}

# Tamil consonants (18 consonants + Grantha letters)
# க ங ச ஞ ட ண த ந ப ம ய ர ல வ ழ ள ற ன
# Grantha: ஜ ஷ ஸ ஹ ஶ ஶ்ரீ க்ஷ (used in Sanskrit loanwords)
CONSONANTS = set('கஙசஞடணதநபமயரலவழளறனஜஷஸஹஶ')

# Pulli (virama) - marks consonant without inherent vowel
PULLI = '்'

def convert_to_phoneme(word_text: str) -> str:
    """
    Convert Tamil word to phonemic representation by decomposing
    consonant+vowel combinations.

    All consonant+vowel combinations are decomposed into:
    [consonant] + [்] + [independent_vowel]

    Special cases (returns None to skip):
    - Words containing '_' (compound word markers)
    - Words containing '-' (grammatical particle markers)

    Args:
        word_text: Tamil word in standard written form

    Returns:
        Phonemic representation with decomposed consonants, or None if word should be skipped

    Examples:
        >>> convert_to_phoneme('ஒல்லென')
        'ஒல்ல்என்அ'

        >>> convert_to_phoneme('அறம்')
        'அற்அம்'

        >>> convert_to_phoneme('கால்')
        'க்ஆல்'

        >>> convert_to_phoneme('தமிழ்')
        'த்அம்இழ்'

        >>> convert_to_phoneme('மயிர்_குறை')
        None

        >>> convert_to_phoneme('விடுநள்-மன்')
        None

        >>> convert_to_phoneme('')
        ''
    """
    if not word_text:
        return word_text

    # Skip words with special markers
    if '_' in word_text or '-' in word_text:
        return None

    result = []
    i = 0

    while i < len(word_text):
        char = word_text[i]

        # Check if this is a consonant
        if char in CONSONANTS:
            # Look ahead for vowel sign or pulli
            if i + 1 < len(word_text):
                next_char = word_text[i + 1]

                if next_char in VOWEL_SIGN_TO_VOWEL:
                    # Consonant + vowel sign → decompose
                    vowel_sign = next_char
                    independent_vowel = VOWEL_SIGN_TO_VOWEL[vowel_sign]

                    result.append(char)
                    result.append(PULLI)
                    result.append(independent_vowel)
                    i += 2  # Skip both consonant and vowel sign
                elif next_char == PULLI:
                    # Consonant + pulli → keep as is (no inherent vowel)
                    result.append(char)
                    result.append(PULLI)
                    i += 2  # Skip both consonant and pulli
                else:
                    # Consonant with inherent 'a' → decompose
                    result.append(char)
                    result.append(PULLI)
                    result.append('அ')
                    i += 1
            else:
                # Consonant at end of string with inherent 'a' → decompose
                result.append(char)
                result.append(PULLI)
                result.append('அ')
                i += 1
        else:
            # Not a consonant (vowel, pulli, aytham, number, punctuation, etc.)
            # Keep as-is
            result.append(char)
            i += 1

    return ''.join(result)


def test_phoneme_converter():
    """Test cases for phoneme converter"""
    print("=" * 70)
    print("Tamil Phoneme Converter - Test Cases")
    print("=" * 70)
    print()

    test_cases = [
        # (input, expected_output, description)
        ('ஒல்லென', 'ஒல்ல்என்அ', 'Original example - geminate consonant with final inherent a'),
        ('அறம்', 'அற்அம்', 'Word with consonant + pulli - decompose ற'),
        ('கால்', 'க்ஆல்', 'Consonant with ா vowel sign'),
        ('தமிழ்', 'த்அம்இழ்', 'Multiple consonant+vowel combinations'),
        ('நன்றி', 'ந்அன்ற்இ', 'Word with consecutive decompositions'),
        ('அ', 'அ', 'Single independent vowel'),
        ('க்', 'க்', 'Single consonant with pulli'),
        ('க', 'க்அ', 'Single consonant (inherent a decomposed)'),
        ('கா', 'க்ஆ', 'Consonant + long aa'),
        ('கி', 'க்இ', 'Consonant + i'),
        ('கீ', 'க்ஈ', 'Consonant + long ii'),
        ('கு', 'க்உ', 'Consonant + u'),
        ('கூ', 'க்ஊ', 'Consonant + long uu'),
        ('கெ', 'க்எ', 'Consonant + e'),
        ('கே', 'க்ஏ', 'Consonant + long ee'),
        ('கை', 'க்ஐ', 'Consonant + ai'),
        ('கொ', 'க்ஒ', 'Consonant + o'),
        ('கோ', 'க்ஓ', 'Consonant + long oo'),
        ('கௌ', 'க்ஔ', 'Consonant + au'),
        ('', '', 'Empty string'),
        ('123', '123', 'Numbers - no change'),
        ('மயிர்_குறை', None, 'Skip compound word marker (_)'),
        ('விடுநள்-மன்', None, 'Skip particle marker (-)'),
        ('கண்_மணி', None, 'Skip compound with _ in middle'),
    ]

    passed = 0
    failed = 0

    for input_word, expected, description in test_cases:
        result = convert_to_phoneme(input_word)
        if result == expected:
            status = 'PASS'
            passed += 1
        else:
            status = 'FAIL'
            failed += 1

        print(f"[{status}] {description}")
        print(f"   Input:    '{input_word}'")
        print(f"   Expected: {expected if expected is not None else 'None (skip)'}")
        print(f"   Got:      {result if result is not None else 'None (skip)'}")

        if result != expected:
            print(f"   ** MISMATCH **")

        print()

    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(test_cases)} total")
    print("=" * 70)

    return failed == 0


if __name__ == '__main__':
    # Run tests when module is executed directly
    success = test_phoneme_converter()
    exit(0 if success else 1)
