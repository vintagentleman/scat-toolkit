import csv
from pathlib import Path
from typing import List, Union

import click

from models.row import Row
from components.normalizer.normalizer import Normalizer

# from components.lemmatizer.lemmatizer import Lemmatizer
from components.writer import Writer
from src import __root__


def parse_tsv(filepath: Path) -> List[Union[str, Row]]:
    with filepath.open(encoding="utf-8", newline="") as fileobject:
        reader = csv.reader(fileobject, delimiter="\t")
        return [
            row[0] if row[0].startswith("<") else Row(filepath.stem, row)
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
    filepaths = list(Path.joinpath(__root__, "scat-content", path).glob(glob))

    manuscripts = {
        manuscript_id: rows
        for manuscript_id, rows in zip(
            [filepath.stem for filepath in filepaths],
            [parse_tsv(filepath) for filepath in filepaths],
        )
    }  # Example: {"DGlush": [Row(), '<head n="1">', ...], "CrlNvz": ...}

    Path.joinpath(__root__, "generated").mkdir(exist_ok=True)
    Path.joinpath(__root__, "generated", mode).mkdir(exist_ok=True)

    for manuscript_id in manuscripts:
        filepath = Path.joinpath(__root__, "generated", mode, f"{manuscript_id}.{mode}")
        writer = Writer.factory(mode, filepath)

        with writer:
            for row in manuscripts[manuscript_id]:
                if row.word is not None:
                    row.word.norm = Normalizer.normalize(row.word)

                    # if lemma := Lemmatizer.factory(row.word).lemmatize(row.word) is None:
                    #     click.echo(f"Lemmatization failed for row {row}")
                    # row.word.lemma = lemma

                if isinstance(row, Row):
                    writer.write(row)
                elif mode == "xml":
                    writer.stream.feed(row)


if __name__ == "__main__":
    main()
