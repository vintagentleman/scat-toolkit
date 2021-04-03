import re
from pathlib import Path

from fire import Fire

from src import __root__
from _models import Row
from utils import replace_chars
from utils.number import Number


def parse_line(line):
    # line = replace_chars(line, "ABEKMHOPCTXЭaeopcyx", "АВЕКМНОРСТХ+аеорсух")
    nums = line[line.rfind("/") + 1:].split()
    toks = list(filter(bool, re.split(r'(</.+?>|<[a-z].+?">)|\s+', line[: line.rfind("/")])))

    for i in range(len(toks)):
        if not (toks[i].startswith("</") or toks[i].endswith("\">")):
            toks[i] = replace_chars(toks[i], "ABEKMHOPCTXЭaeopcyx", "АВЕКМНОРСТХ+аеорсух")

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
        if (len(toks) > i + 1
                and toks[i + 1].startswith("<")
                and not toks[i + 1].startswith("</")
                and not toks[i + 1].endswith("\">")
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

    return [Row([t, None]) for t in toks], nums


def generate_token(toks, nums):
    nums_done = 0

    for t in toks:
        if t.word == "*":
            num = Number(nums[nums_done])
            yield ("{}\t{}" + "\t" * 5).format(str(t).replace("*", num.text), num.value)
            nums_done += 1
        else:
            yield str(t) + "\t" * 6


def run(inp="*.txt", enc="IBM866"):
    filenames = Path.joinpath(__root__, "inp", "tokenizer").glob(inp)

    for filename in filenames:
        with open(filename, mode="r", encoding=enc) as raw, Path.joinpath(
            __root__, "out", filename.stem + ".tsv"
        ).open(mode="w", encoding="utf-8") as tokenized:
            for line in raw.readlines():
                parsed = parse_line(line)
                for token in generate_token(*parsed):
                    tokenized.write(token + "\n")


if __name__ == "__main__":
    Fire(run)
