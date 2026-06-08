"""Interfaz de línea de comandos para el traductor y diccionario Ido."""

import click
from ido.dictionary import Dictionary
from ido.morphology import MorphologyAnalyzer
from ido.parser import IdoParser
from ido.translation import Translator


@click.group()
def main():
    """Traductor y diccionario interactivo para el idioma artificial Ido."""
    pass


@main.command()
@click.argument('word')
def lookup(word):
    """Consultar palabra en el diccionario.
    
    WORD: Palabra a buscar
    """
    db = Dictionary()
    result = db.search_word(word)
    
    if result:
        click.echo(f"\n{result['word']}")
        if result.get('root'):
            click.echo(f"  Morfología: raíz={result['root']}")
            if result.get('affixes'):
                click.echo(f"              afijos={result['affixes']}")
            if result.get('ending'):
                click.echo(f"              terminación={result['ending']}")
        click.echo(f"  Categoría: {result['category']}")
        if result.get('word_type'):
            click.echo(f"  Tipo: {result['word_type']}")
        click.echo(f"  Traducción: {result['translation']}")
    else:
        click.echo(f"No se encontró la palabra: {word}")


@main.command()
@click.argument('word')
def analyze(word):
    """Analizar morfología de una palabra.
    
    WORD: Palabra a analizar
    """
    analyzer = MorphologyAnalyzer()
    analysis = analyzer.analyze(word)
    
    if not analysis:
        click.echo(f"Análisis no disponible para: {word}")
        return
    
    click.echo(f"\n{'='*60}")
    click.echo(f"Analizando: {analysis.original}")
    click.echo('='*60)
    click.echo(f"\nPalabra original: {analysis.original}")
    click.echo(f"Raíz: {analysis.root}")
    
    if analysis.prefixes:
        click.echo(f"Prefijos: {' + '.join(analysis.prefixes)}")
        for prefix in analysis.prefixes:
            meaning = analyzer.PREFIXES.get(prefix, 'desconocido')
            click.echo(f"  - {prefix}: {meaning}")
    
    if analysis.suffixes:
        click.echo(f"Sufijos: {' + '.join(analysis.suffixes)}")
        for suffix in analysis.suffixes:
            meaning = analyzer.SUFFIXES.get(suffix) or analyzer.PARTICIPLES.get(suffix, 'desconocido')
            click.echo(f"  - {suffix}: {meaning}")
    
    if analysis.ending:
        click.echo(f"Terminación: {analysis.ending}")
    
    click.echo(f"\nCategoría: {analysis.category}")
    
    if analysis.subcategories:
        click.echo(f"Subcategorías: {', '.join(analysis.subcategories)}")


@main.command()
@click.argument('phrase')
def parse(phrase):
    """Analizar sintácticamente una frase.
    
    PHRASE: Frase a analizar
    """
    parser = IdoParser()
    try:
        tree = parser.parse(phrase)
        click.echo(f"\n{'='*60}")
        click.echo(f"Analizando: {phrase}")
        click.echo('='*60)
        click.echo(f"\nÁrbol sintáctico:\n{tree.pretty()}")
    except Exception as e:
        click.echo(f"Error al analizar la frase: {e}")


@main.command()
@click.argument('text')
def translate(text):
    """Traducir texto del inglés al Ido.
    
    TEXT: Texto en inglés a traducir
    """
    translator = Translator()
    try:
        # La lógica interna de Translator debe estar adaptada para
        # recibir inglés y devolver la traducción al Ido.
        result = translator.translate(text)
        click.echo(f"\n{'='*60}")
        click.echo(f"Traduciendo: {text}")
        click.echo('='*60)
        click.echo(f"\nTraducción (Inglés → Ido): {result}")
    except Exception as e:
        click.echo(f"Error al traducir: {e}")


if __name__ == '__main__':
    main()
