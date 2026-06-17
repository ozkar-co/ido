"""Tests for Tatoeba corpus formatting."""

from ido.tatoeba import format_sentence


SAMPLE = {
    "id": 13936469,
    "text": "Il sempre malodoras.",
    "lang": "ido",
    "license": "CC BY 2.0 FR",
    "translations": [
        {
            "id": 8180659,
            "text": "He always stinks.",
            "lang": "eng",
            "is_direct": True,
        }
    ],
}


def test_format_sentence():
    block = format_sentence(SAMPLE)
    assert block is not None
    assert "Il sempre malodoras." in block
    assert "He always stinks." in block
    assert "[direct]" in block


def test_format_sentence_direct_only():
    multi = {
        **SAMPLE,
        "translations": [
            {"text": "Direct.", "lang": "eng", "is_direct": True},
            {"text": "Indirect.", "lang": "eng", "is_direct": False},
        ],
    }
    block = format_sentence(multi, direct_only=True)
    assert "Direct." in block
    assert "Indirect." not in block


def test_format_sentence_no_english():
    assert format_sentence({"id": 1, "text": "Saluto.", "translations": []}) is None
