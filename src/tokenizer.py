import re
from pathlib import Path
from typing import List, Tuple

import click

from models.number import Number
from models.row import Row, WordRow, XMLRow
from src import __root__
from utils import replace_chars
from utils.characters import cyrillic_homoglyphs, latin_homoglyphs


def parse_line(manuscript_id: str, line: str) -> Tuple[List[Row], List[str]]:
    nums = line[line.rfind("/") + 1 :].split()
    toks = list(
        filter(bool, re.split(r'(</.+?>|<[a-z].+?">)|\s+', line[: line.rfind("/")]))
    )

    for i in range(len(toks)):
        if not (toks[i].startswith("</") or toks[i].endswith('">')):
            toks[i] = replace_chars(toks[i], latin_homoglyphs, cyrillic_homoglyphs)

    i = 0

    # Сборка токенов из множества кусков
    while i < len(toks):
        # Межстраничные разрывы
        if toks[i] == "Z":
            toks[i] = " ".join([toks[i], toks[i + 1]])
            del toks[i + 1]

        # Разрывы *до* ошибок: ср. '~АБВZ -123 ГДЖ <АБВZ -123 ГДЕ>'
        elif toks[i].endswith("Z"):
            toks[i] = " ".join([toks[i], toks[i + 1], toks[i + 2]])
            del toks[i + 1 : i + 3]

        # Ошибочные написания
        if (
            len(toks) > i + 1
            and toks[i + 1].startswith("<")
            and not toks[i + 1].startswith("</")
            and not toks[i + 1].endswith('">')
        ):
            corr = toks[i + 1]
            del toks[i + 1]

            # Бывают и множественные
            while ">" not in corr:
                corr += " " + toks[i + 1]
                del toks[i + 1]

            toks[i] = " ".join([toks[i], corr])

        # Висячая пунктуация справа и мелкие разрывы
        if len(toks) > i + 1 and re.match(r"[.,:;\]&\\]+", toks[i + 1]):
            toks[i] += toks[i + 1]
            del toks[i + 1]

        i += 1

    return (
        [
            (XMLRow if t.startswith("<") and t.endswith(">") else WordRow)(
                manuscript_id, [t] + [""] * 6
            )
            for t in toks
        ],
        nums,
    )


def generate_token(rows, nums):
    nums_done = 0

    for row in rows:
        if row.source == "*":
            num = Number(nums[nums_done])
            yield f"{row.columns[0].replace('*', num.text)}\t{num.value}\t\t\t\t\t"
            nums_done += 1
        else:
            yield row.tsv()


@click.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    default="raw",
    help="Path to content files, relative to `scat-content` submodule path",
)
@click.option("--encoding", "-e", default="IBM866")
@click.argument("glob", default="*.txt")
def main(path: str, encoding: str, glob: str):
    filepaths = list(Path.joinpath(__root__, "scat-content", path).glob(glob))

    Path.joinpath(__root__, "generated").mkdir(exist_ok=True)
    Path.joinpath(__root__, "generated", "tokenizer").mkdir(exist_ok=True)

    for filepath in filepaths:
        with open(filepath, mode="r", encoding=encoding) as raw, Path.joinpath(
            __root__, "generated", "tokenizer", f"{filepath.stem}.tsv"
        ).open(mode="w", encoding="utf-8") as tokenized:
            for line in raw.readlines():
                parsed = parse_line(filepath.stem, line)
                for token in generate_token(*parsed):
                    tokenized.write(f"{token}\n")


if __name__ == "__main__":
    main()
