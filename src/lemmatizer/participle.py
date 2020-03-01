import re

from utils import lib, letters
from . import Lemmatizer, de_jot, cls_cons_modif


class ParticipleLemmatizer(Lemmatizer):
    def __init__(self, w):
        super().__init__(w)
        self.refl = self.pos.endswith("/в")

        if self.refl:
            self.reg, self.pos = self.reg[:-2], self.pos[:-2]

        if re.match("НЕ(?!ДО)", self.reg):
            self.reg = self.reg[2:]

        if self.reg[-1] not in letters.vows:
            self.reg += "`"

        if "/" in w.msd[0]:
            self.d_old, self.d_new = w.msd[0].split("/")
        else:
            self.d_old = self.d_new = w.msd[0]

        self.tense = w.msd[1]
        self.case = w.msd[2].split("/")[-1]
        self.num = w.msd[3].split("/")[-1]
        self.gen = w.msd[4].split("/")[-1] if w.msd[4] != "0" else "м"

    def _act_past(self):
        # Стемминг
        if self.d_old != "м":
            s_old = self.get_stem(
                (self.d_new, self.case, self.num, self.gen), lib.nom_infl
            )
        else:
            s_old = self.get_stem(
                (self.d_new, self.case, self.num, self.gen), lib.pron_infl
            )

        if s_old is None:
            return self.reg, None

        s_new = s_old

        # Удаление словоизменительных суффиксов
        suff = re.search("В$|В?[ЪЬ]?Ш$", s_new)
        if suff:
            s_new = s_new[: -len(suff.group())]

        # Основы-исключения
        for regex in lib.part_spec:
            mo = re.match(regex, s_new)
            if mo:
                s_modif = re.sub(regex, mo.group(1) + lib.part_spec[regex], s_new)
                if s_new != s_modif:
                    return s_old, s_modif + "ТИ"

        # Проблемные классы
        lemma = cls_cons_modif(s_new)
        if lemma is not None:
            return s_old, lemma

        # Сочетания с йотом
        if s_new.endswith(("Л", "Н", "Р", "Ж", "ЖД", "Ч", "Ш", "ШТ", "Щ")):
            s_new = de_jot(s_new) + "И"
        # 4 класс
        elif s_new[-1] in letters.cons or s_new in ("ВЯ", "СТЫ"):
            s_new += "НУ"

        return s_old, s_new + "ТИ"

    def _pas_past(self):
        # Стемминг
        if self.d_old != "тв":
            s_old = self.get_stem(
                (self.d_new, self.case, self.num, self.gen), lib.nom_infl
            )
        else:
            s_old = self.get_stem(
                (self.d_new, self.case, self.num, self.gen), lib.pron_infl
            )

        if s_old is None:
            return self.reg, None

        s_new = s_old

        # Удаление словоизменительных суффиксов
        suff = re.search("Е?Н?Н$|Т$", s_new)
        if suff:
            s_new = s_new[: -len(suff.group())]

        # Проблемные классы
        lemma = cls_cons_modif(s_new[:-1] + letters.palat_1.get(s_new[-1], s_new[-1]))
        if lemma is not None:
            return s_old, lemma

        # Сочетания с йотом
        if s_new.endswith(("Л", "Н", "Р", "Ж", "ЖД", "Ч", "Ш", "ШТ", "Щ")):
            s_new = de_jot(s_new) + "И"

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

        if self.tense == "прош":
            # Страдательные
            if self.d_old in ("a", "o", "тв"):
                stem, lemma = self._pas_past()
            # Действительные
            else:
                stem, lemma = self._act_past()

        if lemma not in (None, []) and self.refl:
            lemma += "СЯ"

        return stem, lemma
