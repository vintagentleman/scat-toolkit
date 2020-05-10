import re

import utils.infl
import utils.spec
from utils import letters
from .adjective import Adjective


class Numeral(Adjective):
    @staticmethod
    def _pron_modif(stem):
        if re.match("В[ЪЬ]?С$", stem):
            return "ВЕС"
        if re.match("В[ЪЬ]?Ш$", stem):
            return "ВАШ"
        if re.match("Н[ЪЬ]?Ш$", stem):
            return "НАШ"
        if re.match("(К|ОБ|М|СВ|Т|ТВ)О$", stem):
            return stem[:-1]
        if stem in ("С", "СИ"):
            return "СЕ"
        if stem == "Н":
            return ""
        return stem

    def _neg(self, stem):
        if self.neg is not None:  # Префикс стандартный
            return self.neg.group() + stem
        if stem in ("КТО", "ЧТО") and self.zhe is not None:  # Префикс отсечён предлогом
            return "НИ" + stem
        return stem

    def _zhe(self, infl=""):
        return infl if self.zhe is None else infl + self.zhe.group()

    def get_infl(self, stem):
        if self.d_old in ("тв", "м"):
            if stem.startswith("ЕДИН"):
                return "Ъ"
            elif re.match("(Д[ЪЬ]?В|ОБ)$", stem):
                return "А"
            # Собирательные числительные и нумерализованные прилагательные
            return "Е" if stem.endswith(letters.vows) else "О"
        else:
            if stem.startswith("ТР"):
                return "И"
            elif stem.startswith("ЧЕТЫР"):
                return "Е"
            return super().get_infl(stem)

    def get_lemma(self):
        if self.pos == "мест":
            # Проверка на исключительность
            if (
                re.match("К[ОЪ]$", self.reg)
                and self.zhe is not None
                and "Д" in self.zhe.group()
            ):
                return self.reg, self._neg("КО") + self._zhe()
            # Проверка на вопросительность
            if (self.d_old, self.case) in utils.infl.pron_interr and re.match(
                utils.infl.pron_interr[(self.d_old, self.case)][0], self.reg
            ):
                if self.zhe is not None and "Д" in self.zhe.group():
                    return self.reg, self._neg("КО") + self._zhe()
                return (
                    self.reg,
                    self._neg(utils.infl.pron_interr[(self.d_old, self.case)][1])
                    + self._zhe(),
                )
        else:
            # Проверка на изменяемость обеих частей
            for key in utils.spec.numeral:
                if re.match(key, self.reg):
                    return self.reg, utils.spec.numeral[key]

        if self.d_old != "р/скл":
            # Сначала ищем в местоименной парадигме
            s_old = self.get_stem(
                self.reg,
                (self.d_new, self.case, self.num, self.gen),
                utils.infl.pronoun,
            )

            # Если не нашли, то обращаемся к именной (актуально прежде всего для им. и вин. п.)
            if s_old is None:
                if self.d_new == "тв":
                    s_old = self.get_stem(
                        self.reg,
                        (
                            "o" if self.gen in ("м", "ср") else "a",
                            self.case,
                            self.num,
                            self.gen,
                        ),
                        utils.infl.noun,
                    )
                elif self.d_new == "м":
                    s_old = self.get_stem(
                        self.reg,
                        (
                            "jo" if self.gen in ("м", "ср") else "ja",
                            self.case,
                            self.num,
                            self.gen,
                        ),
                        utils.infl.noun,
                    )
                else:
                    s_old = self.get_stem(
                        self.reg,
                        (
                            self.d_new,
                            self.case,
                            self.num,
                            "м"
                            if self.d_new in ("a", "ja", "i") and self.gen == "ср"
                            else self.gen,
                        ),
                        utils.infl.noun,
                    )
        else:
            s_old = self.get_stem(
                self.reg,
                (
                    "тв"
                    if (self.case, self.num, self.gen)
                    in (("тв", "ед", "м"), ("тв", "ед", "ср"))
                    or self.num == "мн"
                    else "м",
                    self.case,
                    self.num,
                    self.gen,
                ),
                utils.infl.pronoun,
            )

            if s_old is None:
                s_old = self.get_stem(
                    self.reg,
                    (
                        "jo" if self.gen in ("м", "ср") else "ja",
                        self.case,
                        self.num,
                        self.gen,
                    ),
                    utils.infl.noun,
                )

        # Обработка основы
        if s_old is None:
            return self.reg, None

        # Модификация основы
        s_new = self._pron_modif(s_old)

        # Плюс-минус
        s_new = self.check_reduction_markup(s_new)

        # Вторая палатализация
        if "*" in self.nb and s_new[-1] in "ЦЗСТ":
            s_new = s_new[:-1] + letters.palat_2[s_new[-1]]

        # Нахождение флексии
        if self.pos == "мест":
            infl = (
                utils.spec.pronoun[s_new]
                if s_new in utils.spec.pronoun
                else super().get_infl(s_new)
            )
        else:
            infl = self.get_infl(s_new)

        return s_old, self._neg(s_new) + self._zhe(infl)
