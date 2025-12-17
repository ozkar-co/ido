"""
Tests para el analizador morfológico.
"""

import pytest
from ido.morphology import MorphologyAnalyzer, MorphologicalAnalysis


class TestMorphologyAnalyzer:
    """Tests para MorphologyAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture para crear un analizador."""
        return MorphologyAnalyzer()
    
    def test_simple_noun(self, analyzer):
        """Test análisis de sustantivo simple."""
        result = analyzer.analyze("abad.o")
        assert result.root == "abad"
        assert result.ending == "o"
        assert result.category == "NOUN (singular)"
        assert result.suffixes == []
        assert result.prefixes == []
    
    def test_noun_with_suffix(self, analyzer):
        """Test sustantivo con sufijo."""
        result = analyzer.analyze("abad.in.o")
        assert result.root == "abad"
        assert result.ending == "o"
        assert result.suffixes == ["in"]
        assert "feminine" in result.subcategories
    
    def test_noun_with_place_suffix(self, analyzer):
        """Test sustantivo con sufijo de lugar."""
        result = analyzer.analyze("abad.ey.o")
        assert result.root == "abad"
        assert result.ending == "o"
        assert result.suffixes == ["ey"]
        assert "place for" in result.subcategories
    
    def test_adjective(self, analyzer):
        """Test adjetivo."""
        result = analyzer.analyze("bel.a")
        assert result.root == "bel"
        assert result.ending == "a"
        assert result.category == "ADJECTIVE"
    
    def test_verb_infinitive(self, analyzer):
        """Test verbo infinitivo."""
        result = analyzer.analyze("vid.ar")
        assert result.root == "vid"
        assert result.ending == "ar"
        assert result.category == "VERB (infinitive)"
    
    def test_verb_with_suffix(self, analyzer):
        """Test verbo con sufijo."""
        result = analyzer.analyze("bel.es.ar")
        assert result.root == "bel"
        assert result.ending == "ar"
        assert result.suffixes == ["es"]
        assert "to be" in result.subcategories
    
    def test_prefix_negation(self, analyzer):
        """Test palabra con prefijo de negación."""
        result = analyzer.analyze("ne.bel.a")
        assert result.root == "bel"
        assert result.prefixes == ["ne"]
        assert result.ending == "a"
    
    def test_prefix_contrary(self, analyzer):
        """Test palabra con prefijo contrario."""
        result = analyzer.analyze("des.facil.a")
        assert result.root == "facil"
        assert result.prefixes == ["des"]
        assert result.ending == "a"
    
    def test_participle_present_active(self, analyzer):
        """Test participio presente activo."""
        result = analyzer.analyze("vid.ant.a")
        assert result.root == "vid"
        assert result.suffixes == ["ant"]
        assert result.ending == "a"
        assert result.category == "PARTICIPLE (adjective form)"
        assert "present active participle" in result.subcategories
    
    def test_participle_past_passive(self, analyzer):
        """Test participio pasado pasivo."""
        result = analyzer.analyze("vid.it.a")
        assert result.root == "vid"
        assert result.suffixes == ["it"]
        assert result.ending == "a"
        assert "past passive participle" in result.subcategories
    
    def test_solid_word_with_prefix(self, analyzer):
        """Test palabra sin puntos con prefijo."""
        result = analyzer.analyze("nebela")
        assert result.root == "bel"
        assert result.prefixes == ["ne"]
        assert result.ending == "a"
    
    def test_solid_word_with_suffix(self, analyzer):
        """Test palabra sin puntos con sufijo."""
        result = analyzer.analyze("beleta")
        assert result.root == "bel"
        assert "et" in result.suffixes  # smallness
        assert result.ending == "a"
    
    def test_verb_present_tense(self, analyzer):
        """Test verbo en presente."""
        result = analyzer.analyze("vid.as")
        assert result.root == "vid"
        assert result.ending == "as"
        assert result.category == "VERB (present)"
    
    def test_verb_past_tense(self, analyzer):
        """Test verbo en pasado."""
        result = analyzer.analyze("vid.is")
        assert result.root == "vid"
        assert result.ending == "is"
        assert result.category == "VERB (past)"
    
    def test_verb_future_tense(self, analyzer):
        """Test verbo en futuro."""
        result = analyzer.analyze("vid.os")
        assert result.root == "vid"
        assert result.ending == "os"
        assert result.category == "VERB (future)"
    
    def test_verb_conditional(self, analyzer):
        """Test verbo condicional."""
        result = analyzer.analyze("vid.us")
        assert result.root == "vid"
        assert result.ending == "us"
        assert result.category == "VERB (conditional)"
    
    def test_verb_imperative(self, analyzer):
        """Test verbo imperativo."""
        result = analyzer.analyze("vid.ez")
        assert result.root == "vid"
        assert result.ending == "ez"
        assert result.category == "VERB (imperative)"
    
    def test_plural_noun(self, analyzer):
        """Test sustantivo plural."""
        result = analyzer.analyze("abad.i")
        assert result.root == "abad"
        assert result.ending == "i"
        assert result.category == "NOUN (plural)"
    
    def test_adverb(self, analyzer):
        """Test adverbio."""
        result = analyzer.analyze("bel.e")
        assert result.root == "bel"
        assert result.ending == "e"
        assert result.category == "ADVERB"


class TestDerivations:
    """Tests para las derivaciones directas."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture para crear un analizador."""
        return MorphologyAnalyzer()
    
    def test_verb_to_noun(self, analyzer):
        """Test derivación verbo a sustantivo."""
        result = analyzer.apply_derivation("brosar", "verb", "noun")
        assert result == "broso"
    
    def test_adjective_to_noun(self, analyzer):
        """Test derivación adjetivo a sustantivo."""
        result = analyzer.apply_derivation("bona", "adjective", "noun")
        assert result == "bono"
    
    def test_noun_to_adjective(self, analyzer):
        """Test derivación sustantivo a adjetivo."""
        result = analyzer.apply_derivation("oro", "noun", "adjective")
        assert result == "ora"
    
    def test_adjective_to_adverb(self, analyzer):
        """Test derivación adjetivo a adverbio."""
        result = analyzer.apply_derivation("bela", "adjective", "adverb")
        assert result == "bele"
    
    def test_dotted_verb_to_noun(self, analyzer):
        """Test derivación con palabra con puntos."""
        result = analyzer.apply_derivation("bros.ar", "verb", "noun")
        assert result == "bros.o"
    
    def test_invalid_derivation(self, analyzer):
        """Test derivación inválida."""
        result = analyzer.apply_derivation("bela", "adjective", "verb")
        assert result is None


class TestVerbForms:
    """Tests para generación de formas verbales."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture para crear un analizador."""
        return MorphologyAnalyzer()
    
    def test_verb_forms_generation(self, analyzer):
        """Test generación de formas verbales."""
        forms = analyzer.get_verb_forms("vid")
        
        assert forms['present_infinitive'] == "vidar"
        assert forms['past_infinitive'] == "vidir"
        assert forms['future_infinitive'] == "vidor"
        assert forms['present'] == "vidas"
        assert forms['past'] == "vidis"
        assert forms['future'] == "vidos"
        assert forms['conditional'] == "vidus"
        assert forms['imperative'] == "videz"


class TestParticiples:
    """Tests para formas participiales."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture para crear un analizador."""
        return MorphologyAnalyzer()
    
    def test_participle_forms_adjective(self, analyzer):
        """Test formas participiales adjetivales."""
        forms = analyzer.get_participle_forms("vid", "a")
        
        assert forms['present_active'] == "vid.ant.a"
        assert forms['past_active'] == "vid.int.a"
        assert forms['future_active'] == "vid.ont.a"
        assert forms['present_passive'] == "vid.at.a"
        assert forms['past_passive'] == "vid.it.a"
        assert forms['future_passive'] == "vid.ot.a"
    
    def test_participle_forms_adverb(self, analyzer):
        """Test formas participiales adverbiales."""
        forms = analyzer.get_participle_forms("vid", "e")
        
        assert forms['present_active'] == "vid.ant.e"
        assert forms['past_active'] == "vid.int.e"
        assert forms['future_active'] == "vid.ont.e"
    
    def test_participle_forms_noun(self, analyzer):
        """Test formas participiales nominales."""
        forms = analyzer.get_participle_forms("vid", "o")
        
        assert forms['present_active'] == "vid.ant.o"
        assert forms['past_passive'] == "vid.it.o"
