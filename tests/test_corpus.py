"""Tests for Tatoeba corpus reader."""

from pathlib import Path

from corpus import iter_tatoeba, load_tatoeba_sentences


SAMPLE = """\
# comment
=== 1 ===
license: CC BY 2.0
ido: Il esas bona.
eng: He is good. [direct]
eng: Indirect.

=== 2 ===
ido: Me amas vu.
eng: I love you.
"""


def test_iter_tatoeba(tmp_path: Path):
    path = tmp_path / "tatoeba.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    entries = list(iter_tatoeba(path))
    assert len(entries) == 2
    assert entries[0].id == 1
    assert entries[0].ido == "Il esas bona."
    assert entries[0].english == ("He is good.", "Indirect.")
    assert entries[1].ido == "Me amas vu."


def test_load_tatoeba_sentences(tmp_path: Path):
    path = tmp_path / "tatoeba.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    sentences = load_tatoeba_sentences(path)
    assert sentences == ["Il esas bona.", "Me amas vu."]
