import re

from utils import lib, letters, replace_chars
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

        if self.mood == "изъяв":
            self.tense, self.num = w.ana[1], w.ana[3].split("/")[-1]
            self.pers, self.gen = (
                (w.ana[2], "") if w.ana[2].isnumeric() else ("", w.ana[2])
            )
            self.role, self.cls = (
                ("", w.ana[4].split("/")[-1]) if w.ana[4].isnumeric() else (w.ana[4], "")
            )
        elif self.mood == "сосл":
            self.pers, self.gen = (
                (w.ana[1], "") if w.ana[1].isnumeric() else ("", w.ana[1])
            )
            self.num, self.role = w.ana[2].split("/")[-1], w.ana[3]
        else:
            self.pers, self.num, self.cls = w.ana[1], w.ana[2], w.ana[3].split("/")[-1]

    def _part_el(self):
        # Стемминг
        s_old = self.get_stem(self.reg, (self.gen, self.num), lib.part_el_infl)

        if s_old is None:
            return self.reg, None

        s_new = s_old

        # Основы-исключения
        for regex in lib.part_el_spec:
            mo = re.match(regex, s_new)
            if mo:
                s_modif = re.sub(regex, mo.group(1) + lib.part_el_spec[regex], s_new)
                if s_new != s_modif:
                    return s_old, s_modif + "ТИ"

        # Проблемные классы
        lemma = self.cls_cons_modif(s_new)
        if lemma is not None:
            return s_old, lemma

        # 4 класс
        if s_new[-1] in letters.cons or s_new in ("ВЯ", "СТЫ"):
            s_new += "НУ"

        return s_old, s_new + "ТИ"

    def _aor_simp(self):
        # Стемминг
        s_old = self.get_stem(self.reg, (self.pers, self.num), lib.aor_simp_infl)

        if s_old is None:
            return self.reg, None

        s_new = s_old

        # Основы-исключения (настоящего времени)
        if s_new.endswith(("ДАД", "ЖИВ", "ИД", "ЫД")):
            s_new = s_new[:-1]

        # Первая палатализация
        if s_new[-1] in "ЧЖШ":
            s_new = s_new[:-1] + letters.palat_1[s_new[-1]]

        # Проблемные классы
        lemma = self.cls_cons_modif(s_new)
        if lemma is not None:
            return s_old, lemma

        # 4 класс
        if s_new[-1] in letters.cons or s_new in ("ВЯ", "СТЫ"):
            s_new += "НУ"

        return s_old, s_new + "ТИ"

    def _aor_sigm(self):
        # Простейший случай
        if self.tense == "аор гл" and self.pers in ("2", "3") and self.num == "ед":
            mo = re.search("С?Т[ЪЬ`]$", self.reg)
            if mo:
                return self.reg, self.reg[: -len(mo.group())] + "ТИ"
            return self.reg, self.reg + "ТИ"

        # Стемминг
        s_old = self.get_stem(self.reg, (self.pers, self.num), lib.aor_sigm_infl)

        if s_old is None:
            return self.reg, None

        # Осложнение тематического суффикса
        if self.tense == "аор нов" and s_old.endswith("О"):
            s_old = s_old[:-1]
        elif self.tense == "аор гл":
            return s_old, s_old + "ТИ"

        s_new = s_old

        # Основы-исключения (настоящего времени)
        if s_new.endswith(("ДАД", "ЖИВ", "ИД", "ЫД")):
            s_new = s_new[:-1]

        # Удлинение корневого гласного
        if self.tense == "аор сигм" and s_new == "Р+":
            return s_old, "РЕЩИ"

        # Проблемные классы
        lemma = self.cls_cons_modif(s_new)
        if lemma is not None:
            return s_old, lemma

        # 4 класс
        if s_new[-1] in letters.cons or s_new in ("ВЯ", "СТЫ"):
            s_new += "НУ"

        return s_old, s_new + "ТИ"

    def _present(self):
        s_old = self.get_stem(
            self.reg,
            (self.pers, self.num),
            lib.pres_infl if self.mood == "изъяв" else lib.imperative_infl
        )

        if s_old is None:
            return self.reg, None

        s_new = s_old

        # 5 класс (словарь)
        if self.cls == "5" or s_new.endswith("БУД"):
            for stem in lib.cls_5:
                if s_new.endswith(stem):
                    # Учёт приставочных дериватов
                    prefix = s_new[: -len(stem)] if len(s_new) != len(stem) else ""
                    return s_old, prefix + lib.cls_5[stem] + "ТИ"
            return s_old, None

        # Удаление тематических гласных
        if ((self.mood == "изъяв" and (self.pers, self.num) not in (("1", "ед"), ("3", "мн")))
                or (self.mood == "повел" and (self.pers, self.num) != ("2", "ед"))):
            s_new = s_new[:-1]

        # 1 класс (алгоритм + словари)
        if self.cls == "1":
            # Основы на согласный
            lemma = self.cls_cons_modif(
                s_new[:-1] + letters.palat_1.get(s_new[-1], s_new[-1])
            )
            if lemma is not None:
                return s_new, lemma

            # Чередование носовых
            if s_new.endswith(("ЕМ", "ЕН", "ИМ", "ИН")):
                s_new = s_new[:-2] + "Я"
            elif s_new.endswith(("М", "Н")):
                s_new = s_new[:-1] + (
                    "А" if s_new[:-1].endswith(letters.cons_hush) else "Я"
                )

            # Сочетания с йотом
            elif s_new.endswith(("Л", "Н", "Р", "Ж", "ЖД", "Ч", "Ш", "ШТ", "Щ")):
                s_new = self.de_jot(s_new) + "И"

            # Основы со вставкой
            elif s_new.endswith(("ДАД", "ЖИВ", "ИД", "ЫД")):
                s_new = s_new[:-1]

            # Чередование /u:/
            else:
                mo = re.search("[ОЪ]?В$", s_new)

                if mo:
                    s_new = s_new[: -len(mo.group())]

                    if s_new[-1] == "З":
                        s_new += "ВА"
                    elif s_new[-1] == "Н":
                        s_new += "У"
                    else:
                        s_new += "Ы"
                else:
                    s_new += "И"

        # 2 класс (алгоритм)
        elif self.cls == "2":
            if s_new.endswith(("Д+Н", "СТАН")):
                s_new = s_new[:-1]
            else:
                s_new += "У"

        # 3 класс (вручную)
        elif self.cls == "3":
            if s_new.endswith("У"):
                return s_old, s_new[:-1] + "ОВАТИ"
            return s_old, s_new + "ТИ"

        # 4 класс (вручную + варианты)
        elif self.cls == "4":
            if s_new.endswith(("Л", "Н", "Р", "Ж", "ЖД", "Ч", "Ш", "ШТ", "Щ")):
                s_new = de_jot(s_new)
            return s_old, [s_new + "ЯТИ", s_new + "+ТИ", s_new + "ИТИ"]

        return s_old, s_new + "ТИ"

    def _imperfect(self):
        stem = self.get_stem(self.reg, (self.pers, self.num), lib.imperfect_infl)

        if stem is None:
            return self.reg, None

        return stem, []

    def get_lemma(self):
        stem, lemma = self.reg, None

        if self.mood == "изъяв":
            # Простые времена
            if self.tense == "н/б":
                stem, lemma = self._present()
            elif self.tense == "имп":
                stem, lemma = self._imperfect()
            elif self.tense == "прош":
                stem, lemma = self._part_el()
            elif self.tense == "аор пр":
                stem, lemma = self._aor_simp()
            elif self.tense.startswith("аор"):
                stem, lemma = self._aor_sigm()
            elif self.tense == "а/имп":
                # Тут лексема одна-единственная
                if self.pers in ("2", "3") and self.num == "ед":
                    s_old = self.reg
                else:
                    s_old = self.get_stem(
                        self.reg, (self.pers, self.num), lib.aor_sigm_infl
                    )

                if s_old is not None:
                    stem, lemma = s_old, "БЫТИ"

            # Сложные времена
            elif re.match("перф|плюскв|буд ?[12]", self.tense):
                if self.role.endswith("св"):
                    if self.tense in lib.ana_tenses:
                        return self.reg, lib.ana_tenses[self.tense]
                    return self.reg, None
                elif self.role == "инф":
                    return self.reg, self.reg
                elif self.role.startswith("пр"):
                    stem, lemma = self._part_el()

        elif self.mood == "сосл":
            if self.role == "св":
                return self.reg, "AUX-SBJ"
            elif self.role.startswith("пр"):
                stem, lemma = self._part_el()

        elif self.mood == "повел":
            stem, lemma = self._present()

        if lemma not in (None, []) and self.refl:
            if isinstance(lemma, list):
                lemma = [var + "СЯ" for var in lemma]
            else:
                lemma += "СЯ"

        return stem, lemma

    @property
    def value(self):
        return []  # TODO
