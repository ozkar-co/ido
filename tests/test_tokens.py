"""Tests del tokenizador y del etiquetado léxico."""

from tokens import split_sentences, tokenize_sentence


def _types(sentence: str) -> list[str]:
    return [token.type for token in tokenize_sentence(sentence)]


def test_nouns_are_not_verbs():
    tokens = tokenize_sentence("La hundo mordas la kato.")
    assert tokens[1].type == "NOUN"
    assert tokens[1].lemma == "hundo"
    assert tokens[4].type == "NOUN"
    assert tokens[4].lemma == "kato"


def test_conjugated_verb_resolves_to_lemma():
    token = tokenize_sentence("Me manjas pano.")[1]
    assert token.type == "VFIN"
    assert token.lemma == "manjar"
    assert "present" in token.features


def test_plural_and_accusative():
    tokens = tokenize_sentence("La kato vidas la hundon.")
    assert tokens[4].type == "NOUN"
    assert tokens[4].lemma == "hundo"
    assert "accusative" in tokens[4].features


def test_proper_names_and_question_words():
    tokens = tokenize_sentence("Quon Maria imaginas?")
    assert tokens[0].type == "QU"
    assert tokens[1].type == "NAME"


def test_nonstandard_copula_is_marked():
    token = tokenize_sentence("Me es feliz.")[1]
    assert token.type == "COP"
    assert token.known is False


def test_conjunction_ed():
    assert "CONJ" in _types("Il esis il e el esis elu.")


def test_compound_lookup_with_hyphen():
    token = tokenize_sentence("La suspektito esis sen-kulpa.")[3]
    assert token.type == "ADJ"
    assert token.lemma == "senkulpa"


def test_number_and_time():
    tokens = tokenize_sentence("Ni venos ye 2:30.")
    assert any(token.type == "NUM" and token.value == "2:30" for token in tokens)


def test_split_sentences():
    parts = split_sentences("Me manjas. Me dormas!")
    assert len(parts) == 2


def test_split_sentences_splits_quoted_sentences():
    parts = split_sentences('"Me manjas." "Me dormas."')
    assert len(parts) == 2
