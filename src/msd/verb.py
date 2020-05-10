import re

import utils.infl
import utils.spec
import utils.verbs
from utils import letters, replace_chars, skip_none
from .msd import Verbal


class Verb(Verbal):
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
                ("", w.ana[4].split("/")[-1])
                if w.ana[4].isnumeric()
                else (w.ana[4], "")
            )
        elif self.mood == "сосл":
            self.pers, self.gen = (
                (w.ana[1], "") if w.ana[1].isnumeric() else ("", w.ana[1])
            )
            self.num, self.role = w.ana[2].split("/")[-1], w.ana[3]
        else:
            self.pers, self.num, self.cls = w.ana[1], w.ana[2], w.ana[3].split("/")[-1]

        self.nb = w.ana[4] if self.mood == "повел" else ""

    @skip_none
    def _part_el(self, s_old):
        if s_old is None:
            return self.reg, None

        s_new = s_old

        # Основы-исключения
        s_modif = self.get_spec_stem(s_new, utils.spec.part_el)
        if s_new != s_modif:
            return s_old, s_modif + "ТИ"

        # Основы на согласный
        lemma = self.modify_cons_stem(s_new)
        if lemma is not None:
            return s_old, lemma

        # 4 класс
        if s_new[-1] in letters.cons or s_new in utils.verbs.cls_iv_vow:
            s_new += "НУ"

        return s_old, s_new + "ТИ"

    @skip_none
    def _aor_simp(self, s_old):
        s_new = s_old

        # Основы настоящего времени
        if s_new.endswith(utils.verbs.cls_vii_2):
            s_new = s_new[:-1]

        # Первая палатализация
        if s_new[-1] in "ЧЖШ":
            s_new = s_new[:-1] + letters.palat_1[s_new[-1]]

        # Основы на согласный
        lemma = self.modify_cons_stem(s_new)
        if lemma is not None:
            return s_old, lemma

        # 4 класс
        if s_new[-1] in letters.cons or s_new in utils.verbs.cls_iv_vow:
            s_new += "НУ"

        return s_old, s_new + "ТИ"

    def _aor_sigm(self, s_old):
        # Простейший случай
        if self.tense == "аор гл" and self.pers in ("2", "3") and self.num == "ед":
            mo = re.search("С?Т[ЪЬ`]$", self.reg)
            if mo:
                return self.reg, self.reg[: -len(mo.group())] + "ТИ"
            return self.reg, self.reg + "ТИ"

        if s_old is None:
            return s_old, None

        # Осложнение тематического суффикса
        if self.tense == "аор нов" and s_old.endswith("О"):
            s_old = s_old[:-1]
        elif self.tense == "аор гл":
            return s_old, s_old + "ТИ"

        s_new = s_old

        # Основы настоящего времени
        if s_new.endswith(utils.verbs.cls_vii_2):
            s_new = s_new[:-1]

        # Удлинение корневого гласного
        if self.tense == "аор сигм" and s_new == "Р+":
            return s_old, "РЕЩИ"

        # Основы на согласный
        lemma = self.modify_cons_stem(s_new)
        if lemma is not None:
            return s_old, lemma

        # 4 класс
        if s_new[-1] in letters.cons or s_new in utils.verbs.cls_iv_vow:
            s_new += "НУ"

        return s_old, s_new + "ТИ"

    @skip_none
    def _present(self, s_old):
        s_new = s_old

        # 5 класс (словарь)
        if self.cls == "5" or s_new.endswith("БУД"):
            for stem in utils.verbs.isol:
                if s_new.endswith(stem):
                    # Учёт приставочных дериватов
                    prefix = s_new[: -len(stem)] if len(s_new) != len(stem) else ""
                    return s_old, prefix + utils.verbs.isol[stem] + "ТИ"

        # Удаление тематических гласных
        if (
            self.mood == "изъяв"
            and (self.pers, self.num) not in (("1", "ед"), ("3", "мн"))
        ) or (self.mood == "повел" and (self.pers, self.num) != ("2", "ед")):
            s_new = s_new[:-1]

        # Вторая палатализация
        if self.mood == "повел" and "*" in self.nb:
            s_new = s_new[:-1] + letters.palat_2.get(s_new[-1], s_new[-1])

            if s_new == "РК":
                s_new = "РЕК"

        # 1 класс (алгоритм + словари)
        if self.cls == "1":
            # Основы на согласный
            lemma = self.modify_cons_stem(
                s_new[:-1] + letters.palat_1.get(s_new[-1], s_new[-1])
            )
            if lemma is not None:
                return s_new, lemma

            # Чередование /u:/
            mo = re.search("[ОЪ]?В$", s_new)
            if mo:
                s_new = s_new[: -len(mo.group())]

                if s_new[-1] == "З":
                    s_new += "ВА"
                elif s_new[-1] == "Н":
                    s_new += "У"
                else:
                    s_new += "Ы"

            # Чередование носовых
            elif s_new.endswith(("ЕМ", "ЕН", "ИМ", "ИН")):
                s_new = s_new[:-2] + "Я"
            elif s_new.endswith(("М", "Н")):
                s_new = s_new[:-1] + (
                    "А" if s_new[:-1].endswith(letters.cons_hush) else "Я"
                )

            # Основы со вставкой
            elif s_new.endswith(utils.verbs.cls_vii_2):
                s_new = s_new[:-1]

            # Приставочные дериваты БЫТИ
            elif s_new.endswith("БУД"):
                s_new = "БЫ"

            elif s_new.endswith(letters.cons):
                s_new = (
                    s_new[:-2] + s_new[-1] + "А"
                    if s_new.endswith(utils.verbs.cls_v_1_d)
                    else s_new + "А"
                )

        # 2 класс (алгоритм)
        elif self.cls == "2":
            if s_new.endswith(utils.verbs.cls_vii_3):
                s_new = s_new[:-1]
            else:
                s_new += "У"

        # 3 класс (авгоритм + словари)
        elif self.cls == "3":
            if s_new.endswith(letters.vows):
                if s_new.endswith("У"):
                    s_new = s_new[:-1] + (
                        "ЕВА" if s_new.endswith(letters.cons_hush) else "ОВА"
                    )
            else:
                # Сочетания с йотом
                if s_new.endswith(letters.cons_hush) or s_new.endswith(
                    letters.cons_sonor
                ):
                    s_new = self.modify_jotted_stem(s_new)

                # Чередование носовых
                if s_new.endswith(("ЕМ", "ЕН", "ИМ", "ИН")):
                    s_new = s_new[:-2] + "Я"

                elif s_new.endswith(letters.cons):
                    s_new += "+" if s_new == "ХОТ" else "А"

        # 4 класс (словарь)
        elif self.cls == "4":
            if s_new.endswith(letters.cons_hush) or s_new.endswith(letters.cons_sonor):
                s_new = self.modify_jotted_stem(s_new)

            if any(re.search(regex + "$", s_new) for regex in utils.verbs.cls_x_e):
                s_new += "+"
            elif any(re.search(regex + "$", s_new) for regex in utils.verbs.cls_x_a):
                s_new += "А" if s_new.endswith(letters.cons_hush) else "Я"
            else:
                s_new += "И"

        return s_old, s_new + "ТИ"

    @skip_none
    def _imperfect(self, s_old):
        # Удаление нестяжённых вокалических сочетаний
        stretch = re.search(r"([+Е][АЯ]|АА|ЯЯ)$", s_old)
        if stretch:
            s_old = s_old[:-2] + s_old[-1]

        s_new = s_old[:-1]

        # Основы-исключения
        for regex in utils.spec.imperfect:
            mo = re.match(regex, s_new)
            if mo:
                s_modif = re.sub(
                    regex, mo.group(1) + utils.spec.imperfect[regex], s_new
                )
                if s_new != s_modif:
                    return s_old, s_modif + "ТИ"

        # Основы на согласный
        lemma = self.modify_cons_stem(
            s_new[:-1] + letters.palat_1.get(s_new[-1], s_new[-1])
        )
        if lemma is not None:
            return s_old, lemma

        # Сочетания с йотом
        s_modif = self.modify_jotted_stem(s_new)
        if s_new != s_modif:
            return s_new, s_modif + "ИТИ"

        # Второе спряжение
        if s_new in utils.verbs.cls_x_a:
            return s_new, s_new + "АТИ"
        if s_new in utils.verbs.cls_x_e:
            return s_new, s_new + "+ТИ"

        # Иначе возвращаем форму на гласную
        return s_old, s_old + "ТИ"

    def get_lemma(self):
        stem, lemma = self.reg, None

        if hasattr(self, "role") and self.role == "св":
            if self.mood == "сосл":
                return self.reg, "AUX-SBJ"
            if self.tense == "перф":
                return self.reg, "AUX-PRF"
            if self.tense == "плюскв":
                return self.reg, "AUX-PQP"

            mo = re.match(r"буд ?([12])", self.tense)
            if mo:
                return self.reg, "AUX-FT" + mo.group(1)
            return self.reg, None

        if self.mood == "изъяв":
            # Простые времена

            if self.tense == "н/б":
                stem, lemma = self._present(
                    self.get_stem(self.reg, (self.pers, self.num), utils.infl.present)
                )
            elif self.tense == "имп":
                stem, lemma = self._imperfect(
                    self.get_stem(self.reg, (self.pers, self.num), utils.infl.imperfect)
                )
            elif self.tense == "прош":
                stem, lemma = self._part_el(
                    self.get_stem(self.reg, (self.gen, self.num), utils.infl.part_el)
                )
            elif self.tense == "аор пр":
                stem, lemma = self._aor_simp(
                    self.get_stem(
                        self.reg, (self.pers, self.num), utils.infl.aorist_simple
                    )
                )
            elif self.tense.startswith("аор"):
                stem, lemma = self._aor_sigm(
                    self.get_stem(
                        self.reg, (self.pers, self.num), utils.infl.aorist_sigm
                    )
                )

            elif self.tense in ("буд", "а/имп"):
                # Тут лексема одна-единственная
                if self.tense == "буд":
                    s_old = self.get_stem(
                        self.reg, (self.pers, self.num), utils.infl.present
                    )
                else:
                    s_old = (
                        self.reg
                        if self.pers in ("2", "3") and self.num == "ед"
                        else self.get_stem(
                            self.reg, (self.pers, self.num), utils.infl.aorist_sigm
                        )
                    )

                if s_old is not None:
                    stem, lemma = s_old, "БЫТИ"

            # Сложные времена
            elif re.match("перф|плюскв|буд ?[12]", self.tense):
                if self.role == "инф":
                    return self.reg, self.reg
                if self.role.startswith("пр"):
                    stem, lemma = self._part_el(
                        self.get_stem(self.reg, (self.gen, self.num), utils.infl.part_el)
                    )

        elif self.mood == "сосл" and self.role.startswith("пр"):
            stem, lemma = self._part_el(
                self.get_stem(self.reg, (self.gen, self.num), utils.infl.part_el)
            )

        elif self.mood == "повел":
            stem, lemma = self._present(
                self.get_stem(self.reg, (self.pers, self.num), utils.infl.imperative)
            )

        if lemma is not None and self.refl:
            lemma += "СЯ"

        return stem, lemma

    @property
    def value(self):
        return []  # TODO
