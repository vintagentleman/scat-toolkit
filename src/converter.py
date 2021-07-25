import csv
from pathlib import Path
from typing import List, Optional, Union

import click

from models.row import Row
from components.normalizer.normalizer import Normalizer

from components.lemmatizer import lemmatizer_factory
from components.writer import Writer
from src import __root__


class Text:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.manuscript_id = filepath.stem

        self.rows: Optional[List[Union[str, Row]]] = None

    def parse_rows(self):
        with self.filepath.open(encoding="utf-8", newline="") as fileobject:
            reader = csv.reader(fileobject, delimiter="\t")
            self.rows = [
                row[0] if row[0].startswith("<") else Row(self.manuscript_id, row)
                for row in reader
            ]


@click.command()
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["txt", "xml"]),  # "proiel.xml", "conll"
    default="xml",
    help="Conversion output format",
)
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    default="annotation/morphological",
    help="Path to content files, relative to `scat-content` submodule path",
)
@click.argument("glob", default="*.tsv")
def main(mode: str, path: str, glob: str):
    # Create text objects
    filepaths = list(Path.joinpath(__root__, "scat-content", path).glob(glob))
    texts = [Text(filepath) for filepath in filepaths]

    # Do all text processing
    [t.parse_rows() for t in texts]

    Path.joinpath(__root__, "generated").mkdir(exist_ok=True)
    Path.joinpath(__root__, "generated", mode).mkdir(exist_ok=True)

    for text in texts:
        filepath = Path.joinpath(
            __root__, "generated", mode, f"{text.manuscript_id}.{mode}"
        )
        writer = Writer.factory(mode, filepath)

        with writer:
            for row in text.rows:
                if row.word is not None:
                    row.word.norm = Normalizer.normalize(row.word)

                    if (
                        lemma := lemmatizer_factory(row.word).lemmatize(row.word)
                    ) is None and not row.word.pos.startswith(("гл", "прич")):
                        click.echo(
                            f"[{text.manuscript_id}] Lemmatization failed for row {row} {row.word.tagset}"
                        )
                    row.word.lemma = lemma

                if isinstance(row, Row):
                    writer.write(row)
                elif mode == "xml":
                    writer.stream.feed(row)


if __name__ == "__main__":
    main()
