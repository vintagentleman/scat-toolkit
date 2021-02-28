import re
from xml.sax.saxutils import escape

from src import __metadata__
from modif.modif import modif
from msd import *
from utils import letters, count_chars, replace_chars, replace_overline_chars
from utils.number import Number


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
        self.br = re.search(r"[&\\%]$|Z\s+(-?\d+)$", word)
        if self.br is not None:
            word = word[: self.br.start()].strip()

        # Конечные знаки препинания
        self.pcr = re.search(r"[.,:;\]]+$", word)
        if self.pcr is not None:
            word, self.pcr = word[: self.pcr.start()].strip(), self.pcr.group()
        else:
            self.pcr = ""

        self.word = word

    def __str__(self):
        return self.src


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

    def is_cardinal_number(self):
        return hasattr(self, "pos") and self.pos.isnumeric()

    def is_ordinal_number(self):
        return hasattr(self, "pos") and self.pos == "числ/п" and "#" in self.src

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
        reg = re.sub(r"(Z\s+-?\d+\s+|[\[\]%&\\])", "", reg).strip().upper()

        # Для цифири нормализация на этом заканчивается
        if self.is_cardinal_number():
            return self.pos
        if self.is_ordinal_number():
            return str(Number(reg.replace("(", "").replace(")", "").replace(" ", "")))

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

        pb = re.search(r"Z\s+(-?\d+)\s+", self.src)

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
                r"\\|Z\s+-?\d+\s+",
                f'<pb n="{metadata["page"] + metadata["column"]}"/><lb n="1"/>',
                res,
            )

        return self._replace_ascii(res)

    @property
    def corr(self):
        if "<" in self.src:
            return self._replace_ascii(
                re.sub(
                    r"(Z\s+-?\d+ ?|[*~\[\]%&\\])",
                    "",
                    self.src[self.src.index("<") + 1 : self.src.index(">")],
                )
            )
        return self._replace_ascii(re.sub(r"(Z\s+-?\d+ ?|[*~\[\]%&\\])", "", self.src))

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

    @property
    def lemma(self):
        if not hasattr(self, "pos"):
            return "None"
        if self.is_cardinal_number():
            return self.pos
        return self.msd.lemma

    def __repr__(self):
        res = f'<w xml:id="{self.doc}.{self.idx}"'

        if hasattr(self, "pos") and not self.is_cardinal_number():
            res += f' pos="{self.pos}"'

            if self.ana[0]:
                res += f' msd="{";".join(elem for elem in self.ana if elem)}"'

        if hasattr(self, "lemma"):
            res += f' lemma="{str(self.lemma).lower()}"'

        res += f' reg="{self.reg.lower()}" src="{escape(self.src)}">{self.orig}</w>'

        if "*" in self.src:
            res = f"<name>{res}</name>"
        elif hasattr(self, "pos") and (
            self.is_cardinal_number() or self.is_ordinal_number()
        ):
            res = f"<num>{res}</num>"

        if "<" in self.src:
            res += f'<note type="corr">{self.corr}</note>'

        return res


class ProielWord(Word):
    @property
    def part_of_speech(self):
        if self.pos == "сущ":
            # Unfortunately, the PROIEL spec does not support
            # animacy for other parts of speech e.g. adjectives
            return "Ne" if "*" in self.src else "Nb"

        if self.pos == "мест":
            # SCAT does not support a more fine-grained distinction
            # other than personal, reflexive, and everything else
            if self.ana[0] == "личн":
                return "Pk" if self.ana[1] == "возвр" else "Pp"
            return "Px"

        if self.pos.startswith("прил"):
            return "A-"

        if self.pos.startswith("числ"):
            return "Mo" if self.pos == "числ/п" else "Ma"

        # Verbal distinctions are encoded in the mood property
        if self.pos.startswith(("гл", "прич", "инф", "суп")):
            return "V-"

        if self.pos == "нар":
            return "Df"

        # PROIEL does not discern between pre- and postpositions
        if self.pos in ("пред", "посл"):
            return "R-"

        if self.pos == "союз":
            return "C-"

        if self.pos == "част":
            return "G-"

        if self.pos == "межд":
            return "I-"

        return "X-"

    @property
    def morphology(self):
        return "".join(
            [
                self._person,
                self._number,
                self._tense,
                self._mood,
                self._voice,
                self._gender,
                self._case,
                self._degree,
                self._strength,
                self._inflection,
            ]
        )

    @property
    def _person(self):
        if not hasattr(self.msd, "pers") or self.msd.pers == "возвр":
            return "-"
        if self.msd.pers in ("1", "2", "3"):
            return self.msd.pers
        return "x"

    @property
    def _number(self):
        if not hasattr(self.msd, "num") or (hasattr(self.msd, "pers") and self.msd.pers == "возвр"):
            return "-"
        if self.msd.num == "ед":
            return "s"
        if self.msd.num == "мн":
            return "p"
        if self.msd.num == "дв":
            return "d"
        return "x"

    @property
    def _tense(self):
        if not hasattr(self.msd, "tense"):
            return "-"
        if self.msd.tense in ("н/б", "наст"):
            return "p"
        if self.msd.tense.startswith(("аор", "а/имп")):
            return "a"
        if self.msd.tense == "имп":
            return "i"
        if self.msd.tense == "плюскв":
            return "l"
        if self.msd.tense == "перф":
            return "r"
        if self.msd.tense in ("буд", "буд 1"):
            return "f"
        if self.msd.tense == "буд 2":
            return "t"
        if self.msd.tense == "прош":
            return "u"
        return "x"

    @property
    def _mood(self):
        if self.pos.startswith("прич"):
            return "p"
        if self.pos.startswith("инф"):
            return "n"
        if self.pos == "суп":
            return "u"

        if not hasattr(self.msd, "mood"):
            return "-"
        if self.msd.mood == "изъяв":
            return "i"
        if self.msd.mood == "повел":
            return "m"
        if self.msd.mood == "сосл":
            return "s"
        return "x"

    @property
    def _voice(self):
        if not self.pos.startswith(("гл", "прич", "инф")):
            return "-"
        if self.pos.endswith("/в"):
            return "p"
        if (
            self.pos == "прич"
            and hasattr(self.msd, "d_old")
            and self.msd.d_old in ("a", "o", "тв")
        ):
            return "p"
        return "a"  # Note active voice by default

    @property
    def _gender(self):
        if not hasattr(self.msd, "gen") or (self.pos.startswith("гл") and hasattr(self.msd, "mood") and self.msd.mood != "сосл"):
            return "-"
        if self.msd.gen == "м":
            return "m"
        if self.msd.gen == "ж":
            return "f"
        if self.msd.gen == "ср":
            return "n"
        return "x"

    @property
    def _case(self):
        if not hasattr(self.msd, "case"):
            return "-"
        if self.msd.case == "им":
            return "n"
        if self.msd.case == "род":
            return "g"
        if self.msd.case == "дат":
            return "d"
        if self.msd.case == "вин":
            return "a"
        if self.msd.case == "тв":
            return "i"
        if self.msd.case == "мест":
            return "l"
        if self.msd.case == "зв":
            return "v"
        return "x"

    @property
    def _degree(self):
        if not self.pos.startswith("прил") or self.pos == "прил/н":
            return "-"
        return "c" if self.pos == "прил/ср" else "p"

    @property
    def _strength(self):
        if not self.pos.startswith(("прил", "прич")) or self.pos == "прил/н":
            return "-"
        if hasattr(self.msd, "d_new"):
            return "s" if self.msd.d_new in ("тв", "м") else "w"
        return "t"

    @property
    def _inflection(self):
        return (
            "i"
            if self.pos.startswith(
                ("сущ", "мест", "прил", "числ", "гл", "прич", "инф", "суп")
            ) and self.pos != "прил/н"
            else "n"
        )
