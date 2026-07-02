import csv
from datetime import date
from pathlib import Path
from typing import List

import click

from components.lemmatizer import lemmatizer_factory
from components.normalizer.normalizer import Normalizer
from components.writer import writer_factory
from models.row import Row, WordRow, XMLRow

__root__ = Path(__file__).resolve().parents[1]


class Text:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.manuscript_id = filepath.stem

        self.rows: List[Row] = []

    def parse_rows(self):
        with self.filepath.open(encoding="utf-8", newline="") as fileobject:
            reader = csv.reader(fileobject, delimiter="\t")

            for i, line in enumerate(reader):
                if line[0].startswith("<"):
                    row = XMLRow(self.manuscript_id, line)
                else:
                    row = WordRow(self.manuscript_id, line)

                    if row.word is not None:
                        row.word.norm = Normalizer.normalize(row.word)

                    if row.word is not None and row.word.tagset is not None:
                        if (
                            lemma := lemmatizer_factory(row.word).lemmatize(row.word)
                        ) is None:
                            click.echo(
                                f"[{self.manuscript_id}] Lemmatization failed for row {i + 1}: {row} {row.word.pos};{row.word.tagset}"
                            )
                        row.word.lemma = lemma

                self.rows.append(row)


@click.command()
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["txt", "tsv", "pkl", "xml"]),
    default="xml",
    help="Conversion output format",
)
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    default="scat-content/annotation/morphological",
    help="Path to content files",
)
@click.argument("glob", default="*.tsv")
def main(mode: str, path: str, glob: str):
    # Create text objects
    filepaths = list(Path.joinpath(__root__, path).glob(glob))
    texts = [Text(filepath) for filepath in filepaths]

    Path.joinpath(__root__, "generated").mkdir(exist_ok=True)
    Path.joinpath(__root__, "generated", "converter").mkdir(exist_ok=True)
    Path.joinpath(__root__, "generated", "converter", mode).mkdir(exist_ok=True)

    for text in texts:
        # Do all row parsing, normalization, and lemmatization
        text.parse_rows()

        # Version shelves by date timestamps rather than manuscript IDs
        # This will also merge the output for all input documents into a single shelf
        filename = date.today().isoformat() if mode == "pkl" else text.manuscript_id
        filepath = Path.joinpath(
            __root__, "generated", "converter", mode, f"{filename}.{mode}"
        )

        with (writer := writer_factory(mode, filepath)):
            [writer.write_row(row) for row in text.rows]


if __name__ == "__main__":
    main()
