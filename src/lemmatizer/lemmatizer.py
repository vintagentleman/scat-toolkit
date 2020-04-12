import re

from utils import lib, letters


class Lemmatizer:
    def __init__(self, w):
        self.reg = w.reg.replace("(", "").replace(")", "")
        self.pos = w.pos

    @staticmethod
    def de_jot(s):
        if s.endswith(("БЛ", "ВЛ", "МЛ", "ПЛ", "ФЛ")):
            return s[:-1]

        elif s.endswith(("Ж", "ЖД")):
            prefix = s[:-2] if s.endswith("ЖД") else s[:-1]

            for suffix in ("Д", "З", "ЗД"):
                for regex in lib.cnj_2_zh:
                    if re.search(regex + "$", prefix + suffix):
                        return prefix + suffix

        elif s.endswith(("Ч", "Щ", "ШТ")):
            prefix = s[:-2] if s.endswith("ШТ") else s[:-1]

            for suffix in ("Т", "СТ"):
                for regex in lib.cnj_2_tsch:
                    if re.search(regex + "$", prefix + suffix):
                        return prefix + suffix

        elif s.endswith("Ш"):
            for regex in lib.cnj_2_sch:
                if re.search(regex + "$", s[:-1] + "С"):
                    return s[:-1] + "С"

        return s

    @staticmethod
    def cls_cons_modif(s):
        # VII.1 класс
        if re.search("(БЛЮ|БРЕ|КЛА|КЛЯ|КРА|ПЛЕ|ВЕ|МЕ|ПА|СЕ|ЧЕ)$", s):
            return s + "СТИ"

        # VI.2.а и VII.1 классы: основы на согласный
        for regex in lib.cnj_1_sti:
            mo = re.match("(.*)%s$" % regex, s)
            if mo:
                return (
                    re.sub("(.*)%s$" % regex, mo.group(1) + lib.cnj_1_sti[regex], s)
                    + "ТИ"
                )

        # VI.1 класс
        for regex in lib.cnj_1_tschi:
            if re.search("%s$" % regex, s):
                s = s[:-1]

                # Чередование с нулём
                if s == "ТОЛ":
                    s += "О"
                elif s == "Ж":
                    s += "Е"

                return s + "ЩИ"

        # VI.2.б и VI.2.в классы
        if re.search("[МПТ][ЕЬ]?Р$", s):
            return s + "ЕТИ"
        elif re.search("ШИБ$", s):
            return s + "ИТИ"

    @staticmethod
    def get_stem(form, msd: tuple, fl_dict: dict):
        if msd in fl_dict:
            fl = re.search("({}|`)$".format(fl_dict[msd]), form)
            return form[: -len(fl.group())] if fl else None
        return None

    def get_lemma(self) -> (str, str):
        lemma = self.reg.replace("(", "").replace(")", "")

        if lemma.endswith(letters.cons):
            lemma += "Ь" if lemma[-1] in letters.cons_hush else "Ъ"

        if self.pos == "пред":
            if lemma in lib.prep_var:
                lemma = lemma[:-1] + "Ъ"

            for regex in lib.prep_rep:
                if re.match(regex, lemma):
                    lemma = re.sub(regex, lib.prep_rep[regex], lemma)

        elif self.pos == "суп":
            lemma = lemma[:-1] + "И"

        return self.reg, lemma
