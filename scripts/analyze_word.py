#!/usr/bin/env python3
"""
Script para analizar la morfología de palabras en Ido.

Permite probar el analizador morfológico con palabras individuales,
mostrando la raíz, prefijos, sufijos, terminaciones y categoría gramatical.

Uso:
    python scripts/analyze_word.py palabra
    python scripts/analyze_word.py abad.o
    python scripts/analyze_word.py bel.es.ant.a
    python scripts/analyze_word.py --derive brosar verb noun
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar el módulo ido
sys.path.insert(0, str(Path(__file__).parent.parent))

from ido.morphology import MorphologyAnalyzer


def print_analysis(analyzer: MorphologyAnalyzer, word: str) -> None:
    """Imprimir análisis de una palabra."""
    print(f"\n{'='*60}")
    print(f"Analizando: {word}")
    print('='*60)
    
    analysis = analyzer.analyze(word)
    
    print(f"\nPalabra original: {analysis.original}")
    print(f"Raíz: {analysis.root}")
    
    if analysis.prefixes:
        print(f"Prefijos: {' + '.join(analysis.prefixes)}")
        for prefix in analysis.prefixes:
            meaning = analyzer.PREFIXES.get(prefix, 'unknown')
            print(f"  - {prefix}: {meaning}")
    
    if analysis.suffixes:
        print(f"Sufijos: {' + '.join(analysis.suffixes)}")
        for suffix in analysis.suffixes:
            meaning = analyzer.SUFFIXES.get(suffix) or analyzer.PARTICIPLES.get(suffix, 'unknown')
            print(f"  - {suffix}: {meaning}")
    
    if analysis.ending:
        print(f"Terminación: {analysis.ending}")
    
    print(f"\nCategoría: {analysis.category}")
    
    if analysis.subcategories:
        print(f"Subcategorías: {', '.join(analysis.subcategories)}")
    
    print()


def demonstrate_derivations(analyzer: MorphologyAnalyzer) -> None:
    """Demostrar las reglas de derivación directa."""
    print("\n" + "="*60)
    print("DEMOSTRACIÓN: Derivaciones Directas")
    print("="*60)
    
    examples = [
        ("brosar", "verb", "noun", "brushing"),
        ("bona", "adjective", "noun", "good one"),
        ("oro", "noun", "adjective", "made of gold"),
        ("bela", "adjective", "adverb", "beautifully"),
    ]
    
    for word, from_type, to_type, meaning in examples:
        derived = analyzer.apply_derivation(word, from_type, to_type)
        print(f"\n{word} ({from_type}) → {derived} ({to_type})")
        print(f"  Meaning: {meaning}")


def demonstrate_verb_forms(analyzer: MorphologyAnalyzer) -> None:
    """Demostrar las formas verbales."""
    print("\n" + "="*60)
    print("DEMOSTRACIÓN: Formas Verbales")
    print("="*60)
    
    root = "vid"  # to see
    print(f"\nRaíz: {root} (to see)")
    print("\nInfinitivos:")
    forms = analyzer.get_verb_forms(root)
    print(f"  Present: {forms['present_infinitive']}")
    print(f"  Past: {forms['past_infinitive']}")
    print(f"  Future: {forms['future_infinitive']}")
    
    print("\nTiempos:")
    print(f"  Present: {forms['present']}")
    print(f"  Past: {forms['past']}")
    print(f"  Future: {forms['future']}")
    print(f"  Conditional: {forms['conditional']}")
    
    print("\nImperativo:")
    print(f"  {forms['imperative']}")


def demonstrate_participles(analyzer: MorphologyAnalyzer) -> None:
    """Demostrar las formas participiales."""
    print("\n" + "="*60)
    print("DEMOSTRACIÓN: Participios")
    print("="*60)
    
    root = "vid"  # to see
    print(f"\nRaíz: {root} (to see)")
    
    # Adjetivos
    print("\nForma adjetival (-a):")
    forms = analyzer.get_participle_forms(root, 'a')
    print(f"  Present active: {forms['present_active']} (seeing)")
    print(f"  Past active: {forms['past_active']} (having seen)")
    print(f"  Future active: {forms['future_active']} (going to see)")
    print(f"  Present passive: {forms['present_passive']} (being seen)")
    print(f"  Past passive: {forms['past_passive']} (having been seen)")
    print(f"  Future passive: {forms['future_passive']} (going to be seen)")
    
    # Adverbios
    print("\nForma adverbial (-e):")
    forms_adv = analyzer.get_participle_forms(root, 'e')
    print(f"  Present active: {forms_adv['present_active']}")
    print(f"  Past active: {forms_adv['past_active']}")


def demonstrate_examples(analyzer: MorphologyAnalyzer) -> None:
    """Mostrar ejemplos de análisis."""
    print("\n" + "="*60)
    print("EJEMPLOS DE ANÁLISIS")
    print("="*60)
    
    examples = [
        "abad.o",         # abbey
        "abad.in.o",      # abbess
        "abad.ey.o",      # abbey (place)
        "bel.a",          # beautiful
        "bel.es.ar",      # to be beautiful
        "bel.ig.ar",      # to beautify
        "ne.bel.a",       # not beautiful
        "des.facil.a",    # difficult
        "mis.komprenar",  # to misunderstand
        "ri.dicar",       # to say again
    ]
    
    for word in examples:
        print_analysis(analyzer, word)


def main() -> None:
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analizar morfología de palabras en Ido',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/analyze_word.py abad.o
  python scripts/analyze_word.py bel.es.ant.a
  python scripts/analyze_word.py --derive brosar verb noun
  python scripts/analyze_word.py --examples
  python scripts/analyze_word.py --demo-verbs
  python scripts/analyze_word.py --demo-participles
        """
    )
    
    parser.add_argument('word', nargs='?', help='Palabra a analizar')
    parser.add_argument('--derive', nargs=3, metavar=('WORD', 'FROM', 'TO'),
                       help='Derivar palabra: palabra tipo_origen tipo_destino')
    parser.add_argument('--examples', action='store_true',
                       help='Mostrar ejemplos de análisis')
    parser.add_argument('--demo-derivations', action='store_true',
                       help='Demostrar derivaciones directas')
    parser.add_argument('--demo-verbs', action='store_true',
                       help='Demostrar formas verbales')
    parser.add_argument('--demo-participles', action='store_true',
                       help='Demostrar formas participiales')
    parser.add_argument('--all-demos', action='store_true',
                       help='Mostrar todas las demostraciones')
    
    args = parser.parse_args()
    
    analyzer = MorphologyAnalyzer()
    
    # Mostrar todas las demos
    if args.all_demos:
        demonstrate_examples(analyzer)
        demonstrate_derivations(analyzer)
        demonstrate_verb_forms(analyzer)
        demonstrate_participles(analyzer)
        return
    
    # Demos individuales
    if args.examples:
        demonstrate_examples(analyzer)
        return
    
    if args.demo_derivations:
        demonstrate_derivations(analyzer)
        return
    
    if args.demo_verbs:
        demonstrate_verb_forms(analyzer)
        return
    
    if args.demo_participles:
        demonstrate_participles(analyzer)
        return
    
    # Derivación
    if args.derive:
        word, from_type, to_type = args.derive
        derived = analyzer.apply_derivation(word, from_type, to_type)
        if derived:
            print(f"\n{word} ({from_type}) → {derived} ({to_type})")
            print("\nAnalysis of derived word:")
            print_analysis(analyzer, derived)
        else:
            print(f"\nError: Cannot derive {word} from {from_type} to {to_type}")
        return
    
    # Análisis de palabra
    if args.word:
        print_analysis(analyzer, args.word)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
