import re
from xml.sax.saxutils import escape

from src import __metadata__
from modif.modif import modif
from msd import *
from utils import letters, count_chars, replace_chars, replace_overline_chars


class Row:
    def __init__(self, row):
        self.src = word = row[0]
        self.ana = row[1:]

        # Начальные знаки препинания
        self.pcl = re.search(r"^[.,:;[]+", word)
        if self.pcl is not None:
            word, self.pcl = word[self.pcl.end() :].strip(), self.pcl.group()
        else:
            self.pcl = ""

        # Висячие разрывы
        self.br = re.search(r"[&\\%]$|Z (-?\d+)$", word)
        if self.br is not None:
            word = word[: self.br.start()].strip()

        # Конечные знаки препинания
        self.pcr = re.search(r"[.,:;\]]+$", word)
        if self.pcr is not None:
            word, self.pcr = word[: self.pcr.start()].strip(), self.pcr.group()
        else:
            self.pcr = ""

        self.word = word


class Word:
    def __init__(self, doc, idx, src, ana=None):
        self.doc, self.idx = doc, idx
        self.src = replace_chars(
            src, "ABEKMHOPCTXЭaeopcyx", "АВЕКМНОРСТХ+аеорсух"
        )  # Latin to Cyr

        if ana is not None:
            self.pos, self.ana = (
                replace_chars(ana[0], "aeopcyx", "аеорсух"),
                ana[1:],
            )  # Latin to Cyr

            if "/" in self.pos and not re.search(r"/([внп]|ср)$", self.pos):
                self.pos = self.pos.split("/")[-1]
            self.msd = self.msd_cls(self)

        if hasattr(self, "pos") and self.pos and not self.pos.isnumeric():
            self.stem, self.lemma = self.msd.get_lemma()
        else:
            self.stem, self.lemma = self.src, None

    @staticmethod
    def _replace_ascii(s):
        s = re.sub(r"\((.+?)\)", replace_overline_chars, s)
        s = replace_chars(s, "IRVWU+FSGDLQЯ$", "їѧѵѡѹѣѳѕѫꙋѯѱꙗ҂")

        if "#" in s:
            s = s.replace("#", "")
            num = int(count_chars(s) > 1)
            s = s[: count_chars(s, num) + 1] + "҃" + s[count_chars(s, num) + 1 :]

        return s.replace("ѡⷮ", "ѿ").lower()

    @staticmethod
    def _replace_izhitsa(s, i):
        try:
            prev_char, next_char = s[i - 1], s[i + 1]
        except IndexError:
            return "И"

        if (
            prev_char == "Е"
            or prev_char in letters.vows
            and next_char in letters.vows + letters.cons_sonor
        ):
            return "В"

        return "И"

    @property
    def reg(self):
        reg = (
            self.src
            if "<" not in self.src
            else self.src[self.src.index("<") + 1 : self.src.index(">")]
        )  # Удаление ошибочных написаний

        # Удаление внутренних разрывов
        reg = re.sub(r"(Z -?\d+ ?|[.,:;%&[\]\\])", "", reg).strip().upper()

        # Для цифири нормализация на этом заканчивается
        if hasattr(self, "pos"):
            if self.pos.isnumeric():
                return self.pos
            if self.pos == "числ/п" and "#" in reg:
                return reg.replace("(", "").replace(")", "")

        prop, corr = reg.startswith("*"), reg.startswith("~")
        if prop or corr:
            reg = reg[1:]

        reg = replace_chars(
            reg, "SIWDGUFRLQ", ("З", "И", "О", "У", "У", "У", "Ф", "Я", "КС", "ПС")
        )  # Остаточная нормализация

        for idx in [
            idx for idx, char in enumerate(reg) if char == "V"
        ]:  # Позиционная замена ижицы
            reg = reg[:idx] + self._replace_izhitsa(reg, idx) + reg[idx + 1 :]

        # Нормализация орфографии
        reg = modif(reg, self.pos if hasattr(self, "pos") else "")

        if prop:
            reg = "*" + reg
        elif corr:
            reg = "~" + reg

        return reg.replace("#", "")

    @property
    def orig(self):
        res = self.src[: self.src.index("<") - 1] if "<" in self.src else self.src
        metadata = __metadata__[self.doc]

        if res.startswith(("*", "~")):
            res = res[1:]  # Удаление маркеров собственности и ошибочности

        # Замена разрывов строк (внутри одной словоформы может быть несколько)
        while "&" in res:
            metadata["line"] += 1
            res = res.replace("&", f'<lb n="{metadata["line"]}"/>', 1)

        pb = re.search(r"Z (-?\d+) ?", self.src)

        # Замена разрывов колонок и/или страниц
        if "\\" in res or pb:
            if "\\" in res:
                metadata["column"] = "b"
            else:
                metadata["page"], metadata["column"] = (
                    pb.group(1),
                    "a" if metadata["column"] else "",
                )

            metadata["line"] = 1
            res = re.sub(
                r"\\|Z -?\d+ ?",
                f'<pb n="{metadata["page"] + metadata["column"]}"/><lb n="1"/>',
                res,
            )

        return self._replace_ascii(res)

    @property
    def corr(self):
        if "<" in self.src:
            return self._replace_ascii(
                re.sub(
                    r"(Z -?\d+ ?|[*~\[\]%&\\])",
                    "",
                    self.src[self.src.index("<") + 1 : self.src.index(">")],
                )
            )

    @property
    def msd_cls(self):
        if self.pos == "сущ":
            return Noun
        if self.pos in ("прил", "прил/ср", "числ/п"):
            return Adjective
        if self.pos == "числ":
            return Numeral
        if self.pos == "мест":
            return Pronoun if self.ana[0] == "личн" else Numeral
        if self.pos in ("гл", "гл/в"):
            return Verb
        if self.pos in ("прич", "прич/в"):
            return Participle
        return MSD

    def __repr__(self):
        res = f'<w xml:id="{self.doc}.{self.idx}"'

        if hasattr(self, "pos") and not self.pos.isnumeric():
            res += f' pos="{self.pos}"'

            if self.ana[0]:
                res += f' msd="{";".join(elem for elem in self.ana if elem)}"'
            if hasattr(self, "lemma"):
                res += f' lemma="{str(self.lemma).lower()}"'

        res += f' reg="{self.reg.lower()}" src="{escape(self.src)}">{self.orig}</w>'

        if "*" in self.src:
            res = f"<name>{res}</name>"
        elif hasattr(self, "pos") and self.pos.isnumeric():
            res = f"<num>{res}</num>"

        if self.corr is not None:
            res += f'<note type="corr">{self.corr}</note>'

        return res
