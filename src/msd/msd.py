import re

import utils.spec
import utils.verbs
from utils import letters


class MSD:
    def __init__(self, w):
        self.reg = w.reg.replace("(", "").replace(")", "")
        self.pos = w.pos

    @staticmethod
    def palat(stem, type_) -> str:
        return (
            stem
            if len(stem) == 1
            else stem[:-1] + getattr(letters, "palat_" + type_).get(stem[-1], stem[-1])
        )

    @staticmethod
    def stem_in_dict(stem, stem_dict) -> bool:
        return any(re.search(regex + "$", stem) for regex in stem_dict)

    @staticmethod
    def get_stem(form, msd: tuple, fl_dict: dict):
        if msd in fl_dict:
            fl = re.search("({}|`)$".format(fl_dict[msd]), form)
            return form[: -len(fl.group())] if fl else None
        return None

    @staticmethod
    def get_spec_stem(stem: str, spec_dict: dict):
        s_modif = stem

        for regex in spec_dict:
            mo = re.match(regex, stem)
            if mo:
                s_modif = re.sub(regex, mo.group(1) + spec_dict[regex], stem)

        return s_modif

    @property
    def lemma(self) -> str:
        lemma = self.reg.replace("(", "").replace(")", "")

        if lemma.endswith(letters.cons):
            lemma += "Ь" if lemma[-1] in letters.cons_hush else "Ъ"

        if self.pos == "пред":
            if lemma in utils.spec.prep_var:
                lemma = lemma[:-1] + "Ъ"

            for regex in utils.spec.prep:
                if re.match(regex, lemma):
                    lemma = re.sub(regex, utils.spec.prep[regex], lemma)

        elif self.pos == "суп":
            lemma = lemma[:-1] + "И"

        return lemma

    def modify_jotted_stem(self, s):
        assert self.pos.startswith(("гл", "прич"))

        if s.endswith(("БЛ", "ВЛ", "МЛ", "ПЛ", "ФЛ")):
            return s[:-1]

        if s.endswith(("Ж", "ЖД")):
            stem = s[:-2] if s.endswith("ЖД") else s[:-1]

            for cons in ("Г", "Д", "З", "ЗД"):
                if any(
                    re.search(regex + "$", stem + cons)
                    for regex in utils.verbs.jotted_zh
                ):
                    return stem + cons

        elif s.endswith(("Ч", "Щ", "ШТ")):
            stem = s[:-2] if s.endswith("ШТ") else s[:-1]

            for cons in ("К", "Т", "СК", "СТ"):
                if any(
                    re.search(regex + "$", stem + cons)
                    for regex in utils.verbs.jotted_tsch
                ):
                    return stem + cons

        elif s.endswith("Ш") and any(
            re.search(regex + "$", s[:-1] + "С") for regex in utils.verbs.jotted_sch
        ):
            return s[:-1] + "С"

        return s

    @staticmethod
    def get_dict_lemma(stem, dict_, suff):
        for regex in dict_:
            mo = re.match(r"(.*){}$".format(regex), stem)
            if mo:
                return (
                    re.sub(r"(.*){}$".format(regex), mo.group(1) + dict_[regex], stem,)
                    + suff
                )
        return None

    def modify_cons_stem(self, s):
        assert self.pos.startswith(("гл", "прич"))

        # Подкласс VII/1
        lemma = self.get_dict_lemma(s, utils.verbs.cls_vii_1, "СТИ")
        if lemma is not None:
            return lemma

        # Группа VI/2/а
        lemma = self.get_dict_lemma(s, utils.verbs.cls_vi_2_a, "ТИ")
        if lemma is not None:
            return lemma

        # Подкласс VI/1
        lemma = self.get_dict_lemma(s, utils.verbs.cls_vi_1, "ЩИ")
        if lemma is not None:
            return lemma

        # Группа VI/2/б
        if re.search("[МПТ][ЕЬ]?Р$", s):
            return s + "+ТИ"

        # Группа VI/2/в
        if re.search("ШИБ$", s):
            return s[:-2] + "ИТИ"

    def modify_uu(self, s):
        assert self.pos.startswith(("гл", "прич"))

        if s.endswith("ЖИВ"):
            return s[:-1]
        if s.endswith("СЛОВ"):
            return s + "И"

        mo = re.search("[ОЪ]?В$", s)
        if mo:
            s = s[: -len(mo.group())]

            if s[-1] == "З":
                s += "ВА"
            elif s[-1] == "Н":
                s += "У"
            else:
                s += "Ы"

        return s

    @property
    def pickled(self):
        return [self.pos]
