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
        self.voice = "пас" if self.d_old in ("a", "o", "тв") else "акт"

    def _act_pres(self, stem, suff) -> str:
        if self.stem_in_dict(stem, utils.verbs.cls_vii_2):
            return self.cls_1(stem)
        if suff in ("Ы", "УЩ"):
            return self.cls_2(stem) if stem.endswith("Н") else self.cls_1(stem)
        if suff == "ЮЩ" or (
            suff == "УЩ" and stem.endswith(letters.cons_hush + letters.cons_sonor)
        ):
            return self.cls_3(stem)
        if suff in ("АЩ", "ЯЩ", "ИЩ"):
            return self.cls_4(stem)
        if stem.endswith(("А", "+")):
            return self.cls_3(stem)
        if suff in ("А", "Я"):
            if stem.endswith(letters.cons_hush) or stem.endswith(letters.cons_sonor):
                stem = self.modify_jotted_stem(stem)

            if self.stem_in_dict(stem, utils.verbs.cls_x_e):
                return stem + "+ТИ"
            if self.stem_in_dict(stem, utils.verbs.cls_x_a):
                return stem + ("А" if stem.endswith(letters.cons_hush) else "Я") + "ТИ"
            if self.stem_in_dict(stem, utils.verbs.cls_x_i):
                return stem + "ИТИ"
            return self.cls_3(stem)
        return "None"

    def _pas_pres(self, stem, suff) -> str:
        if suff == "ОМ":
            return self.cls_1(stem)
        if suff == "ЕМ":
            return self.cls_3(stem)
        if suff == "ИМ":
            return self.cls_4(stem)
        return "None"

    def _act_past(self, stem) -> str:
        # Удаление словоизменительных суффиксов
        suff = re.search("В$|В?[ЕЪЬ]?Ш$", stem)
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
        lemma = self.modify_cons_stem(self.palat(stem, "1"))
        if lemma is not None:
            return lemma

        # Сочетания с йотом
        if stem.endswith(letters.cons_hush + letters.cons_sonor):
            stem = self.modify_jotted_stem(stem) + "И"

        # Чередование /u:/
        elif suff and suff.group().startswith("ЕН"):
            stem = self.modify_uu(stem) if stem[-1] == "В" else stem + "И"

        # 4 класс
        elif stem[-1] in letters.cons or self.stem_in_dict(
            stem, utils.verbs.cls_iv_vow
        ):
            stem += "НУ"

        return stem + "ТИ"

    @property
    def lemma(self) -> str:
        suff = None

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
        elif (self.voice, self.case, self.num, self.gen) not in (
            ("акт", "им", "ед", "м"),
            ("акт", "им", "ед", "ср"),
        ):
            stem = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, self.gen), utils.infl.noun
            )

            if stem is None and self.d_old == "ja":
                stem = self.get_stem(
                    self.reg, ("jo", self.case, self.num, self.gen), utils.infl.noun,
                )
        else:
            stem = self.reg[:-1]
            suff = self.reg[-1]

        if stem is None:
            return "None"

        if self.tense == "наст":
            if suff is None:
                if self.voice == "акт":
                    mo = re.search(r".Щ$", stem)
                    if mo is None:
                        mo = re.search(r"[АЫЯ]$", stem)
                else:
                    mo = re.search(r".М$", stem)

                if mo is not None:
                    suff = mo.group()
                    stem = stem[: -len(suff)]

            # 5 класс
            lemma = self.cls_5(stem)

            if lemma is None:
                # Основы на согласный
                lemma = self.modify_cons_stem(stem)

                if lemma is None:
                    lemma = (
                        self._act_pres(stem, suff)
                        if self.voice == "акт"
                        else self._pas_pres(stem, suff)
                    )

        else:
            lemma = (
                self._act_past(stem) if self.voice == "акт" else self._pas_past(stem)
            )

        if lemma != "None" and self.refl:
            lemma += "СЯ"

        return lemma

    @property
    def pickled(self):
        return [self.pos, self.d_old, self.tense, self.case, self.num, self.gen]
