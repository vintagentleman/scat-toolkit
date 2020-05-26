import re

import utils.infl
import utils.spec
import utils.verbs
from utils import letters, replace_chars, skip_none
from .msd import MSD


class Verb(MSD):
    def __init__(self, w):
        super().__init__(w)
        self.refl = self.pos.endswith("/в")

        if self.refl:
            self.reg, self.pos = self.reg[:-2], self.pos[:-2]

        if self.reg[-1] not in letters.vows:
            self.reg += "`"

        self.mood = replace_chars(w.ana[0], "aeopcyx", "аеорсух")  # Latin to Cyr
        self.mood = self.mood.replace("изьяв", "изъяв")

        if self.mood == "изъяв":
            self.tense, self.num = w.ana[1], w.ana[3].split("/")[-1]
            self.pers, self.gen = (
                (w.ana[2], "") if w.ana[2].isnumeric() else ("", w.ana[2])
            )
            self.role, self.cls = (
                ("", w.ana[4].split("/")[0])
                if w.ana[4].split("/")[0].isnumeric()
                else (w.ana[4], "")
            )
        elif self.mood == "сосл":
            self.pers, self.gen = (
                (w.ana[1], "") if w.ana[1].isnumeric() else ("", w.ana[1])
            )
            self.num, self.role = w.ana[2].split("/")[-1], w.ana[3]
        else:
            self.pers, self.num, self.cls = w.ana[1], w.ana[2], w.ana[3].split("/")[0]

    @skip_none
    def _part_el(self, stem) -> str:
        # Основы-исключения
        s_modif = self.get_spec_stem(stem, utils.spec.part_el)
        if stem != s_modif:
            return s_modif + "ТИ"

        # Основы на согласный
        lemma = self.modify_cons_stem(stem)
        if lemma is not None:
            return lemma

        # 4 класс
        if stem[-1] in letters.cons or stem in utils.verbs.cls_iv_vow:
            stem += "НУ"

        return stem + "ТИ"

    @skip_none
    def _aor_simp(self, stem) -> str:
        # Основы настоящего времени
        if self.stem_in_dict(stem, utils.verbs.cls_vii_2):
            stem = stem[:-1]

        # Первая палатализация
        if stem[-1] in "ЧЖШ":
            stem = self.palat(stem, "1")

        # Основы на согласный
        lemma = self.modify_cons_stem(stem)
        if lemma is not None:
            return lemma

        # 4 класс
        if stem[-1] in letters.cons or stem in utils.verbs.cls_iv_vow:
            stem += "НУ"

        return stem + "ТИ"

    def _aor_sigm(self, stem) -> str:
        # Простейший случай
        if self.tense == "аор гл" and self.pers in ("2", "3") and self.num == "ед":
            mo = re.search("(?<!\+)С?Т[ЪЬ`]$", self.reg)
            if mo:
                return self.reg[: -len(mo.group())] + "ТИ"
            return self.reg + "ТИ"

        if stem is None:
            return "None"

        # Осложнение тематического суффикса
        if self.tense == "аор нов" and stem.endswith("О"):
            stem = stem[:-1]

        if self.tense == "аор гл":
            return (
                stem[:-2]
                if self.stem_in_dict(stem[:-1], utils.verbs.cls_vii_2)
                else stem
            ) + "ТИ"

        # Основы настоящего времени
        if self.stem_in_dict(stem, utils.verbs.cls_vii_2):
            stem = stem[:-1]

        # Удлинение корневого гласного
        if self.tense == "аор сигм" and stem == "Р+":
            return "РЕЩИ"

        # Основы на согласный
        lemma = self.modify_cons_stem(stem)
        if lemma is not None:
            return lemma

        # 4 класс
        if stem[-1] in letters.cons or stem in utils.verbs.cls_iv_vow:
            stem += "НУ"

        return stem + "ТИ"

    def cls_1(self, stem) -> str:
        # Основы на согласный
        lemma = self.modify_cons_stem(
            stem[:-1] + letters.palat_1.get(stem[-1], stem[-1])
        )
        if lemma is not None:
            return lemma

        # Чередование /u:/
        stem = self.modify_uu(stem)

        # Чередование носовых
        nasal = re.search(r"[ЕИ]?[МН]$", stem)
        if nasal:
            stem = stem[: -len(nasal.group())] + (
                "А" if stem[: -len(nasal.group())].endswith(letters.cons_hush) else "Я"
            )

        # Основы со вставкой
        elif self.stem_in_dict(stem, utils.verbs.cls_vii_2):
            stem = stem[:-1]

        # Приставочные дериваты БЫТИ
        elif stem.endswith("БУД"):
            stem = "БЫ"

        elif stem.endswith(letters.cons):
            stem = (
                stem[:-2] + stem[-1] + "А"
                if stem.endswith(utils.verbs.cls_v_1_d)
                else stem + "А"
            )

        return stem + "ТИ"

    def cls_2(self, stem) -> str:
        # Основы на согласный
        lemma = self.modify_cons_stem(stem[:-1])
        if lemma is not None:
            return lemma

        if stem.endswith(utils.verbs.cls_vii_3):
            return stem[:-1] + "ТИ"
        return stem + "УТИ"

    def cls_3(self, stem) -> str:
        if stem.endswith(letters.vows):
            if stem.endswith("У"):
                stem = stem[:-1] + (
                    "ЕВА" if stem.endswith(letters.cons_hush) else "ОВА"
                )
            elif self.stem_in_dict(stem, utils.verbs.cls_v_1_b):
                stem += "Я"
        else:
            # Сочетания с йотом
            if stem.endswith(letters.cons_hush) or stem.endswith(letters.cons_sonor):
                stem = self.modify_jotted_stem(stem)

            # Чередование носовых
            nasal = re.search(r"[ЕИ]?[МН]$", stem)
            if nasal:
                stem = stem[: -len(nasal.group())] + (
                    "А"
                    if stem[: -len(nasal.group())].endswith(letters.cons_hush)
                    else "Я"
                )

            elif self.stem_in_dict(stem, utils.verbs.cls_v_2):
                stem = stem[:-2] + "О" + stem[-1] + "О"

            elif self.stem_in_dict(stem, utils.verbs.cls_viii):
                stem += "ВА"

            elif stem.endswith(letters.cons):
                stem += "+" if stem.endswith("ХОТ") else "А"

        return stem + "ТИ"

    def cls_4(self, stem) -> str:
        if stem.endswith(letters.cons_hush) or stem.endswith(letters.cons_sonor):
            stem = self.modify_jotted_stem(stem)

        if self.stem_in_dict(stem, utils.verbs.cls_x_e):
            stem += "+"
        elif self.stem_in_dict(stem, utils.verbs.cls_x_a):
            stem += "А" if stem.endswith(letters.cons_hush) else "Я"
        else:
            stem += "И"

        return stem + "ТИ"

    @staticmethod
    def cls_5(stem) -> str:
        for regex in utils.verbs.isol:
            mo = re.search(r"{}$".format(regex), stem)
            if mo is not None:
                return stem[: -len(mo.group())] + utils.verbs.isol[regex] + "ТИ"

    @skip_none
    def _present(self, stem) -> str:
        # 5 класс
        if self.cls == "5" or stem.endswith("БУД"):
            lemma = self.cls_5(stem)
            if lemma is not None:
                return lemma

        # Удаление тематических гласных
        if self.mood == "изъяв" and (self.pers, self.num) not in (
            ("1", "ед"),
            ("3", "мн"),
        ):
            stem = stem[:-1]

        try:
            return getattr(self, "cls_" + self.cls)(stem)
        except AttributeError:
            return "None"

    @skip_none
    def _imperative(self, stem) -> str:
        # Удаление тематических гласных
        if (self.pers, self.num) not in (("2", "ед"), ("3", "ед")):
            stem = stem[:-1]

        # Вторая палатализация
        lemma = self.modify_cons_stem(self.palat(stem, "2"))
        if lemma is not None:
            return lemma

        return self._present(stem)

    @skip_none
    def _imperfect(self, stem) -> str:
        # Удаление нестяжённых вокалических сочетаний
        stretch = re.search(r"([+Е][АЯ]|АА|ЯЯ)$", stem)
        if stretch:
            theme = stem[-2]
            stem = stem[:-2]
        else:
            theme = stem[-1]
            stem = stem[:-1]

        # Основы-исключения
        for regex in utils.spec.imperfect:
            mo = re.match(regex, stem)
            if mo:
                s_modif = re.sub(regex, mo.group(1) + utils.spec.imperfect[regex], stem)
                if stem != s_modif:
                    return s_modif + "ТИ"

        # Основы на согласный
        lemma = self.modify_cons_stem(
            stem[:-1] + letters.palat_1.get(stem[-1], stem[-1])
        )
        if lemma is not None:
            return lemma

        # Сочетания с йотом
        s_modif = self.modify_jotted_stem(stem)
        if stem != s_modif:
            return s_modif + "ИТИ"

        # Второе спряжение
        if self.stem_in_dict(stem, utils.verbs.cls_x_e):
            stem += "+"
        elif self.stem_in_dict(stem, utils.verbs.cls_x_a):
            stem += "А" if stem.endswith(letters.cons_hush) else "Я"
        elif self.stem_in_dict(stem, utils.verbs.cls_x_i):
            stem += "И"
        # I/5 подкласс
        elif not self.stem_in_dict(stem, utils.verbs.cls_i_5):
            stem += theme

        return stem + "ТИ"

    @property
    def lemma(self) -> str:
        lemma = "None"

        if hasattr(self, "role") and self.role == "св":
            if self.mood == "сосл":
                return "AUX-SBJ"
            if self.tense == "перф":
                return "AUX-PRF"
            if self.tense == "плюскв":
                return "AUX-PQP"

            mo = re.match(r"буд ?([12])", self.tense)
            if mo:
                return "AUX-FT" + mo.group(1)
            return "None"

        if self.mood == "изъяв":
            # Простые времена

            if self.tense == "н/б":
                lemma = self._present(
                    self.get_stem(self.reg, (self.pers, self.num), utils.infl.present)
                )
            elif self.tense == "имп":
                lemma = self._imperfect(
                    self.get_stem(self.reg, (self.pers, self.num), utils.infl.imperfect)
                )
            elif self.tense == "прош":
                lemma = self._part_el(
                    self.get_stem(self.reg, (self.gen, self.num), utils.infl.part_el)
                )
            elif self.tense == "аор пр":
                lemma = self._aor_simp(
                    self.get_stem(
                        self.reg, (self.pers, self.num), utils.infl.aorist_simple
                    )
                )
            elif self.tense.startswith("аор"):
                lemma = self._aor_sigm(
                    self.get_stem(
                        self.reg, (self.pers, self.num), utils.infl.aorist_sigm
                    )
                )

            elif self.tense in ("буд", "а/имп"):
                # Тут лексема одна-единственная
                if self.tense == "буд":
                    stem = self.get_stem(
                        self.reg, (self.pers, self.num), utils.infl.present
                    )
                else:
                    stem = (
                        self.reg
                        if self.pers in ("2", "3") and self.num == "ед"
                        else self.get_stem(
                            self.reg, (self.pers, self.num), utils.infl.aorist_sigm
                        )
                    )

                if stem is not None:
                    lemma = "БЫТИ"

            # Сложные времена
            elif re.match("перф|плюскв|буд ?[12]", self.tense):
                if self.role == "инф":
                    return self.reg
                if self.role.startswith("пр"):
                    lemma = self._part_el(
                        self.get_stem(
                            self.reg, (self.gen, self.num), utils.infl.part_el
                        )
                    )

        elif self.mood == "сосл" and self.role.startswith("пр"):
            lemma = self._part_el(
                self.get_stem(self.reg, (self.gen, self.num), utils.infl.part_el)
            )

        elif self.mood == "повел":
            lemma = self._imperative(
                self.get_stem(self.reg, (self.pers, self.num), utils.infl.imperative)
            )

        if lemma != "None" and self.refl:
            lemma += "СЯ"

        return lemma

    @property
    def pickled(self):
        if hasattr(self, "gen") and self.gen:
            return [self.pos, "", "", self.gen, self.num]
        if self.lemma == "БЫТИ":
            return [self.pos, "", "", self.pers, self.num]
        if (
            hasattr(self, "tense")
            and re.match(r"(н/б|буд ?1)", self.tense)
            and self.lemma in ("НАЧАТИ", "ХОТ+ТИ", "ИМ+ТИ")
        ):
            return [self.pos, self.mood, "", self.pers, self.num]
        return [
            self.pos,
            self.mood,
            self.tense if hasattr(self, "tense") else "",
            self.pers,
            self.num,
        ]
