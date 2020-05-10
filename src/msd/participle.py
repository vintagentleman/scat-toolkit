import re

import utils.infl
import utils.spec
from utils import letters, replace_chars
from .msd import Verbal


class Participle(Verbal):
    def __init__(self, w):
        super().__init__(w)
        w.ana[0] = replace_chars(w.ana[0], "аеоу", "aeoy")  # Cyr to Latin
        self.refl = self.pos.endswith("/в")

        if self.refl:
            self.reg, self.pos = self.reg[:-2], self.pos[:-2]

        if re.match("НЕ(?!(ДО|НАВИ))", self.reg):
            self.reg = self.reg[2:]

        if self.reg[-1] not in letters.vows:
            self.reg += "`"

        if "/" in w.ana[0]:
            self.d_old, self.d_new = w.ana[0].split("/")
        else:
            self.d_old = self.d_new = w.ana[0]

        self.tense = w.ana[1]
        self.case = w.ana[2].split("/")[-1]
        self.num = w.ana[3].split("/")[-1]
        self.gen = w.ana[4].split("/")[-1] if w.ana[4] != "0" else "м"

    def _act_pres(self):
        return "None"

    def _pas_pres(self):
        return "None"

    def _act_past(self) -> str:
        # Стемминг
        if self.d_old != "м":
            stem = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, self.gen), utils.infl.noun
            )
        else:
            stem = self.get_stem(
                self.reg,
                (self.d_new, self.case, self.num, self.gen),
                utils.infl.pronoun,
            )

        if stem is None:
            return "None"

        # Удаление словоизменительных суффиксов
        suff = re.search("В$|В?[ЪЬ]?Ш$", stem)
        if suff:
            stem = stem[: -len(suff.group())]

        # Основы-исключения
        s_modif = self.get_spec_stem(stem, utils.spec.part)
        if stem != s_modif:
            return s_modif + "ТИ"

        # Проблемные классы
        lemma = self.modify_cons_stem(stem)
        if lemma is not None:
            return lemma

        # Сочетания с йотом
        if stem.endswith(("Л", "Н", "Р", "Ж", "ЖД", "Ч", "Ш", "ШТ", "Щ")):
            stem = self.modify_jotted_stem(stem) + "И"
        # 4 класс
        elif stem[-1] in letters.cons or stem in ("ВЯ", "СТЫ"):
            stem += "НУ"

        return stem + "ТИ"

    def _pas_past(self) -> str:
        # Стемминг
        if self.d_old != "тв":
            stem = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, self.gen), utils.infl.noun
            )
        else:
            stem = self.get_stem(
                self.reg,
                (self.d_new, self.case, self.num, self.gen),
                utils.infl.pronoun,
            )

        if stem is None:
            return "None"

        # Удаление словоизменительных суффиксов
        suff = re.search("Е?Н?Н$|Т$", stem)
        if suff:
            stem = stem[: -len(suff.group())]

        # Проблемные классы
        lemma = self.modify_cons_stem(
            stem[:-1] + letters.palat_1.get(stem[-1], stem[-1])
        )
        if lemma is not None:
            return lemma

        # Сочетания с йотом
        if stem.endswith(("Л", "Н", "Р", "Ж", "ЖД", "Ч", "Ш", "ШТ", "Щ")):
            stem = self.modify_jotted_stem(stem) + "И"

        # Чередование /u:/: 'вдохновенный', 'проникновенный'; 'омовенный', 'незабвенный'. Но - 'благословенный'
        elif suff and suff.group().startswith("ЕН"):
            mo = re.search("[ОЪ]?В$", stem)

            if not stem.endswith("СЛОВ") and mo:
                stem = stem[: -len(mo.group())]

                if stem[-1] == "Н":
                    stem += "У"
                else:
                    stem += "Ы"
            else:
                stem += "И"

        # 4 класс
        elif stem[-1] in letters.cons or stem in ("ВЯ", "СТЫ"):
            stem += "НУ"

        return stem + "ТИ"

    def get_lemma(self) -> str:
        if self.d_old in ("a", "o", "тв"):
            lemma = self._pas_pres() if self.tense == "наст" else self._pas_past()
        else:
            lemma = self._act_pres() if self.tense == "наст" else self._act_past()

        if lemma != "None" and self.refl:
            lemma += "СЯ"

        return lemma

    @property
    def value(self):
        return [self.d_old, self.tense, self.case, self.num, self.gen]
