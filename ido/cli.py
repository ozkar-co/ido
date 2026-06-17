"""Command-line interface for the Ido study tool."""

import click

from ido.db import DatabaseError
from ido.dictionary import Dictionary
from ido.phrases import PhraseStore


@click.group()
def main():
    """Ido language study and practice tools."""
    pass


@main.command("lookup")
@click.argument("word")
def lookup_cmd(word):
    """Look up an Ido word."""
    try:
        db = Dictionary()
    except DatabaseError as exc:
        raise click.ClickException(str(exc)) from exc
    try:
        entry = db.lookup_ido(word)
        if not entry:
            raise click.ClickException(f"Not found: {word}")
        derived = db.list_derived(entry.word)
        click.echo(db.format_entry(entry, derived=derived or None))
    finally:
        db.close()


@main.command("en")
@click.argument("term")
@click.option("-n", "--limit", default=20, show_default=True)
def en_cmd(term, limit):
    """Look up Ido words by English gloss."""
    try:
        db = Dictionary()
    except DatabaseError as exc:
        raise click.ClickException(str(exc)) from exc
    try:
        entries = db.lookup_en(term, limit=limit)
        if not entries:
            raise click.ClickException(f"No matches for: {term}")
        for entry in entries:
            root = entry.root or "?"
            click.echo(f"{entry.word}  (root: {root})")
            click.echo(f"  {entry.translation}\n")
    finally:
        db.close()


@main.command("add-word")
@click.argument("word")
@click.argument("root")
@click.argument("translation")
@click.option("--notes", default=None)
def add_word_cmd(word, root, translation, notes):
    """Add or update a dictionary entry."""
    try:
        db = Dictionary()
    except DatabaseError as exc:
        raise click.ClickException(str(exc)) from exc
    try:
        entry = db.add_word(word, root or None, translation, notes=notes)
        click.echo(db.format_entry(entry))
    finally:
        db.close()


@main.command("phrase-add")
@click.argument("ido")
@click.argument("english")
def phrase_add_cmd(ido, english):
    """Add an Ido-English phrase pair."""
    try:
        store = PhraseStore()
    except DatabaseError as exc:
        raise click.ClickException(str(exc)) from exc
    try:
        phrase = store.add(ido, english)
        click.echo(store.format_phrase(phrase))
        click.echo(f"Total: {store.count()}")
    finally:
        store.close()


@main.command("phrase-count")
def phrase_count_cmd():
    """Show phrase count."""
    try:
        store = PhraseStore()
    except DatabaseError as exc:
        raise click.ClickException(str(exc)) from exc
    try:
        click.echo(store.count())
    finally:
        store.close()


@main.command("phrase-search")
@click.argument("query", default="")
@click.option("--ido", "field_ido", is_flag=True)
@click.option("--en", "field_en", is_flag=True)
@click.option("-n", "--limit", default=20, show_default=True)
def phrase_search_cmd(query, field_ido, field_en, limit):
    """Search stored phrases."""
    field = "both"
    if field_ido:
        field = "ido"
    elif field_en:
        field = "en"

    try:
        store = PhraseStore()
    except DatabaseError as exc:
        raise click.ClickException(str(exc)) from exc
    try:
        phrases = store.search(query, field=field, limit=limit) if query else store.list_recent(limit=limit)
        if not phrases:
            raise click.ClickException("No phrases found.")
        for phrase in phrases:
            click.echo(store.format_phrase(phrase))
            click.echo()
    finally:
        store.close()


if __name__ == "__main__":
    main()
