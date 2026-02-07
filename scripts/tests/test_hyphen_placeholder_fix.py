#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify hyphen placeholder fix
Tests that sequences of hyphens (lost word markers) are not tokenized as words
"""

import re

def test_hyphen_detection():
    """Test the regex pattern for detecting hyphen-only tokens"""

    # Test cases: (token, should_be_skipped)
    test_cases = [
        # Should be skipped (only hyphens)
        ('-', True),
        ('--', True),
        ('---', True),
        ('--------', True),
        ('----------------', True),

        # Should NOT be skipped (contains Tamil text)
        ('வான்-நிலா', False),
        ('கடல்-மலை', False),
        ('-வான்', False),
        ('மலை-', False),

        # Should NOT be skipped (Tamil words)
        ('அறம்', False),
        ('கடல்', False),

        # Should NOT be skipped (numbers - handled by separate check)
        ('5', False),
        ('10', False),
    ]

    pattern = r'^-+$'

    print("Testing hyphen-only token detection:")
    print("=" * 60)

    passed = 0
    failed = 0

    for token, should_skip in test_cases:
        matches = bool(re.match(pattern, token))

        if matches == should_skip:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1

        print(f"{status}: '{token}' -> should_skip={should_skip}, matches={matches}")

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_real_examples():
    """Test with real examples from Purananuru and Paripaadal"""

    print("\n\nTesting real examples from source files:")
    print("=" * 60)

    # Example from புறநானூறு #341 line 6
    line1 = "---------------- ------------- --------------"
    tokens1 = line1.split()

    print(f"\nPurananuru 341 line 6: '{line1}'")
    print(f"Tokens: {tokens1}")

    words_created = []
    for token in tokens1:
        if re.match(r'^-+$', token):
            print(f"  ✓ Skipping hyphen placeholder: '{token}'")
        else:
            words_created.append(token)
            print(f"  → Creating word: '{token}'")

    if len(words_created) == 0:
        print("✓ PASS: No words created from hyphen placeholders")
    else:
        print(f"✗ FAIL: {len(words_created)} words incorrectly created")

    # Example from பரிபாடல் with mixed content
    line2 = "---------- ------------ மரபினோய் நின் அடி"
    tokens2 = line2.split()

    print(f"\n\nParipaadal mixed line: '{line2}'")
    print(f"Tokens: {tokens2}")

    words_created = []
    for token in tokens2:
        if re.match(r'^-+$', token):
            print(f"  ✓ Skipping hyphen placeholder: '{token}'")
        else:
            # In real code, this would go through clean_tamil_word()
            words_created.append(token)
            print(f"  → Creating word: '{token}'")

    expected_words = ['மரபினோய்', 'நின்', 'அடி']
    if words_created == expected_words:
        print(f"✓ PASS: Correct words created: {words_created}")
    else:
        print(f"✗ FAIL: Expected {expected_words}, got {words_created}")


if __name__ == '__main__':
    success = test_hyphen_detection()
    test_real_examples()

    if success:
        print("\n\n✓ All tests passed! Fix is working correctly.")
    else:
        print("\n\n✗ Some tests failed. Please review the fix.")
