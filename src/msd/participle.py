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

    def _act_past(self):
        # Стемминг
        if self.d_old != "м":
            s_old = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, self.gen), utils.infl.noun
            )
        else:
            s_old = self.get_stem(
                self.reg,
                (self.d_new, self.case, self.num, self.gen),
                utils.infl.pronoun,
            )

        if s_old is None:
            return self.reg, None

        s_new = s_old

        # Удаление словоизменительных суффиксов
        suff = re.search("В$|В?[ЪЬ]?Ш$", s_new)
        if suff:
            s_new = s_new[: -len(suff.group())]

        # Основы-исключения
        s_modif = self.get_spec_stem(s_new, utils.spec.part)
        if s_new != s_modif:
            return s_old, s_modif + "ТИ"

        # Проблемные классы
        lemma = self.modify_cons_stem(s_new)
        if lemma is not None:
            return s_old, lemma

        # Сочетания с йотом
        if s_new.endswith(("Л", "Н", "Р", "Ж", "ЖД", "Ч", "Ш", "ШТ", "Щ")):
            s_new = self.modify_jotted_stem(s_new) + "И"
        # 4 класс
        elif s_new[-1] in letters.cons or s_new in ("ВЯ", "СТЫ"):
            s_new += "НУ"

        return s_old, s_new + "ТИ"

    def _pas_past(self):
        # Стемминг
        if self.d_old != "тв":
            s_old = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, self.gen), utils.infl.noun
            )
        else:
            s_old = self.get_stem(
                self.reg,
                (self.d_new, self.case, self.num, self.gen),
                utils.infl.pronoun,
            )

        if s_old is None:
            return self.reg, None

        s_new = s_old

        # Удаление словоизменительных суффиксов
        suff = re.search("Е?Н?Н$|Т$", s_new)
        if suff:
            s_new = s_new[: -len(suff.group())]

        # Проблемные классы
        lemma = self.modify_cons_stem(
            s_new[:-1] + letters.palat_1.get(s_new[-1], s_new[-1])
        )
        if lemma is not None:
            return s_old, lemma

        # Сочетания с йотом
        if s_new.endswith(("Л", "Н", "Р", "Ж", "ЖД", "Ч", "Ш", "ШТ", "Щ")):
            s_new = self.modify_jotted_stem(s_new) + "И"

        # Чередование /u:/: 'вдохновенный', 'проникновенный'; 'омовенный', 'незабвенный'. Но - 'благословенный'
        elif suff and suff.group().startswith("ЕН"):
            mo = re.search("[ОЪ]?В$", s_new)

            if not s_new.endswith("СЛОВ") and mo:
                s_new = s_new[: -len(mo.group())]

                if s_new[-1] == "Н":
                    s_new += "У"
                else:
                    s_new += "Ы"
            else:
                s_new += "И"

        # 4 класс
        elif s_new[-1] in letters.cons or s_new in ("ВЯ", "СТЫ"):
            s_new += "НУ"

        return s_old, s_new + "ТИ"

    def get_lemma(self):
        stem, lemma = self.reg, None

        if self.d_old in ("a", "o", "тв"):
            stem, lemma = self._pas_pres() if self.tense == "наст" else self._pas_past()
        else:
            stem, lemma = self._act_pres() if self.tense == "наст" else self._act_past()

        if lemma is not None and self.refl:
            lemma += "СЯ"

        return stem, lemma

    @property
    def value(self):
        return [self.d_old, self.tense, self.case, self.num, self.gen]
