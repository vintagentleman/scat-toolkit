import re

import utils.infl
import utils.spec
import utils.verbs
from utils import letters, replace_chars
from .verb import Verb


class Participle(Verb):
    def __init__(self, w):
        super(Verb, self).__init__(w)
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

    def _act_pres(self, stem) -> str:
        # Учёт словоизменительных суффиксов
        mo = re.search(
            r"[АЫЯ]$"
            if (self.d_new, self.case, self.num) == ("jo", "им", "ед")
            else r".Щ$",
            stem,
        )
        if mo is None:
            return "None"

        suff = mo.group()
        stem = stem[: -len(suff)]

        lemma = self.modify_cons_stem(stem)
        if lemma is not None:
            return lemma

        if suff == "ЮЩ":
            return self.cls_3(stem)
        if suff in ("А", "Я", "УЩ") and stem.endswith(
            letters.cons_hush + letters.cons_sonor
        ):
            return self.cls_3(stem)
        if suff in ("Ы", "УЩ"):
            return self.cls_2(stem) if stem.endswith("Н") else self.cls_1(stem)
        if suff == "ЯЩ":
            return self.cls_4(stem)
        if suff in ("А", "Я"):  # Здесь невозможно определить, 3 класс или 4
            return self.cls_3(stem)
        return "None"

    def _pas_pres(self, stem) -> str:
        # Учёт словоизменительных суффиксов
        mo = re.search(r".М$", stem)
        if mo is None:
            return "None"

        suff = mo.group()
        stem = stem[: -len(suff)]

        lemma = self.modify_cons_stem(stem)
        if lemma is not None:
            return lemma

        if suff == "ОМ":
            return self.cls_1(stem)
        if suff == "ИМ":
            return self.cls_4(stem)
        return self.cls_3(stem)

    def _act_past(self, stem) -> str:
        # Удаление словоизменительных суффиксов
        suff = re.search("В$|В?[ЪЬ]?Ш$", stem)
        if suff:
            stem = stem[: -len(suff.group())]

        # Основы-исключения
        s_modif = self.get_spec_stem(stem, utils.spec.part)
        if stem != s_modif:
            return s_modif + "ТИ"

        # Основы на согласный
        lemma = self.modify_cons_stem(stem)
        if lemma is not None:
            return lemma

        # Сочетания с йотом
        if stem.endswith(letters.cons_hush + letters.cons_sonor):
            stem = self.modify_jotted_stem(stem) + "И"
        # 4 класс
        elif stem[-1] in letters.cons or stem in utils.verbs.cls_iv_vow:
            stem += "НУ"

        return stem + "ТИ"

    def _pas_past(self, stem) -> str:
        # Удаление словоизменительных суффиксов
        suff = re.search("Е?Н?Н$|Т$", stem)
        if suff:
            stem = stem[: -len(suff.group())]

        # Основы на согласный
        lemma = self.modify_cons_stem(
            stem[:-1] + letters.palat_1.get(stem[-1], stem[-1])
        )
        if lemma is not None:
            return lemma

        # Сочетания с йотом
        if stem.endswith(letters.cons_hush + letters.cons_sonor):
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
        elif stem[-1] in letters.cons or stem in utils.verbs.cls_iv_vow:
            stem += "НУ"

        return stem + "ТИ"

    def get_lemma(self) -> str:
        if self.d_old in ("тв", "м"):
            stem = self.get_stem(
                self.reg,
                (self.d_new, self.case, self.num, self.gen),
                utils.infl.pronoun,
            )

            if stem is None and self.d_old == "м":
                stem = self.get_stem(
                    self.reg, ("тв", self.case, self.num, self.gen), utils.infl.pronoun,
                )
        else:
            stem = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, self.gen), utils.infl.noun
            )

            if stem is None and self.d_old in ("ja", "jo"):
                stem = self.get_stem(
                    self.reg, (self.d_old[1:], self.case, self.num, self.gen), utils.infl.noun
                )

        if stem is None:
            if (self.d_new, self.case, self.num) != ("jo", "им", "ед"):
                return "None"
            stem = self.reg

        if self.d_old in ("a", "o", "тв"):
            return (
                self._pas_pres(stem) if self.tense == "наст" else self._pas_past(stem)
            )
        return self._act_pres(stem) if self.tense == "наст" else self._act_past(stem)

    @property
    def value(self):
        return [self.d_old, self.tense, self.case, self.num, self.gen]
