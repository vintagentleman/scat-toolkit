"""
Usage: python converter.py [--inp="DP.tsv"] [--mode="xml"] run
"""

import json
from pathlib import Path

from fire import Fire
import pandas as pd

from src import __root__
from _models import Row, Word
from _writer import TSVWriter, PKLWriter, XMLWriter, ProielXMLWriter


class Converter:
    def __init__(self, inp="*.tsv", mode="tsv"):
        self.inp = Path.joinpath(__root__, "inp", "converter").glob(inp)
        self.filter = json.load(
            Path.joinpath(__root__, "conf", "filter.json").open(encoding="utf-8")
        )
        self.mode = mode

        if self.mode == "tsv":
            self.writer = TSVWriter
        elif self.mode == "pkl":
            self.writer = PKLWriter
        elif self.mode == "xml":
            self.writer = XMLWriter
        elif self.mode == "proiel.xml":
            self.writer = ProielXMLWriter
        else:
            raise ValueError(
                "--mode should be set to any of: 'tsv', 'pkl', 'xml', or 'proiel.xml'"
            )

    def run(self):
        for filename in self.inp:
            df = pd.read_csv(filename, sep="\t", header=None, na_filter=False)

            if self.filter:
                df = df[
                    eval(
                        " & ".join(
                            f"df[{idx}].isin({self.filter[idx]})" for idx in self.filter
                        )
                    )
                ]

            with self.writer(
                Path.joinpath(
                    __root__,
                    "out",
                    "db" if self.mode == "pkl" else f"{filename.stem}.{self.mode}",
                )
            ) as out:
                for idx, row in df.iterrows():
                    row = Row(row.map(str.strip).to_list())

                    if row.word.startswith("</") or row.word.endswith('">'):
                        out.stream.feed(row.word)
                        df.drop(idx, inplace=True)
                        continue

                    if self.mode.endswith("xml"):
                        out.write(row)
                    else:
                        word = Word(filename.stem, idx, row.word, row.ana)

                        if self.mode == "tsv":
                            if hasattr(word, "pos"):
                                out.write(row.src, word.pos, *word.ana, word.lemma)
                            else:
                                out.write(row.src + "\t" * 7)
                        else:
                            out.write(word.reg, word.msd.pickled)


if __name__ == "__main__":
    Fire(Converter)
