import re

import utils.infl
import utils.spec
from utils import letters, replace_chars
from .msd import MSD


class Noun(MSD):
    def __init__(self, w):
        super().__init__(w)

        if w.pos != "мест":
            w.ana[0] = replace_chars(w.ana[0], "аеоу", "aeoy")  # Cyr to Latin

        # Маркер собственности
        self.prop = "*" in self.reg
        if self.prop:
            self.reg = self.reg[1:]

        # НЕ- и -ЖЕ/-ЖДО
        if self.pos == "мест":
            self.zhe = re.search("ЖЕ$|Ж[ЪЬ]?Д[ЕО]$", self.reg)
            self.neg = re.match("Н[+ЕИ](?=[КЧ])", self.reg)

            if self.zhe:
                self.reg = self.reg[: -len(self.zhe.group())]
            if self.neg:
                self.reg = self.reg[len(self.neg.group()) :]
        else:
            self.zhe = None
            self.neg = None

        # Гласный-пустышка
        if self.reg[-1] not in letters.vows:
            self.reg += "`"

        # Типы склонения: старый для основы, новый для флексии
        if "/" in w.ana[0] and w.ana[0] != "р/скл":
            self.d_old, self.d_new = w.ana[0].split("/")
        else:
            self.d_old = self.d_new = w.ana[0]

        self.case = w.ana[1].split("/")[-1]

        # Pluralia tantum
        self.pt = w.ana[2] == "pt"
        if self.pt:
            self.num = "мн"
        else:
            self.num = w.ana[2].split("/")[-1] if w.ana[2] != "0" else "ед"

        self.gen = w.ana[3].split("/")[-1] if w.ana[3] != "0" else "м"
        self.nb = w.ana[4]

    def _is_reduced(self):
        return (
            self.d_new in ("a", "ja")
            and (self.case, self.num) == ("род", "мн")
            or self.d_new in ("o", "jo")
            and self.gen == "м"
            and (self.case, self.num)
            not in (("им", "ед"), ("вин", "ед"), ("род", "мн"))
            or self.d_new in ("o", "jo")
            and self.gen == "ср"
            and (self.case, self.num) == ("род", "мн")
            or self.d_new in ("i", "u")
            and (self.case, self.num) not in (("им", "ед"), ("вин", "ед"))
            or self.d_new.startswith("e")
            and (self.case, self.num)
            not in (("им", "ед"), ("вин", "ед"), ("род", "мн"))
            or self.d_new == "uu"
            and (self.case, self.num)
            not in (("им", "ед"), ("вин", "ед"), ("род", "мн"))
        )

    def _de_reduce_manual(self, stem):
        if "+о" in self.nb:
            stem = stem[:-1] + "О" + stem[-1]
        elif "+е" in self.nb:
            stem = stem[:-1] + "Е" + stem[-1]
        else:
            stem = stem[:-2] + stem[-1]

        return stem

    def _de_reduce_auto(self, stem):
        if self.d_old == "ja" and stem[-2] == "Е":
            stem = stem[:-2] + stem[-1]
        elif self.d_old == "jo" and stem[-2] in letters.cons:
            stem = stem[:-1] + "Е" + stem[-1]

        return stem

    def __remove_suffix(self, stem):
        for th in utils.spec.noun_them_suff:
            if th in (self.d_old, self.d_new):
                suffix = re.search(utils.spec.noun_them_suff[th], stem)
                if suffix:
                    stem = stem[: -len(suffix.group())]

        return stem

    def __add_suffix(self, stem):
        if self.d_old == "en" and not (
            stem.endswith("ЕН") or re.match("Д[ЪЬ]?Н", stem)
        ):
            suffix = re.search(utils.spec.noun_them_suff[self.d_old], stem)
            if suffix:
                stem = stem[: -len(suffix.group())]
            stem += "ЕН"

        elif self.d_old == "uu" and not stem.endswith("ОВ"):
            suffix = re.search(utils.spec.noun_them_suff[self.d_old], stem)
            if suffix:
                stem = stem[: -len(suffix.group())]
            stem += "ОВ"

        return stem

    def _decl_spec_modif(self, stem):
        # Удаление/добавление тематических суффиксов
        if {self.d_old, self.d_new} & {"ent", "men", "es", "er"}:
            stem = self.__remove_suffix(stem)
        elif self.d_old in ("en", "uu"):
            stem = self.__add_suffix(stem)

        # Плюс-минус
        stem = self.check_reduction_markup(stem)

        if stem == "ХРИСТ":
            stem += "ОС"

        # Для слова 'БРАТЪ' во мн. ч. - минус Ь или И
        if (self.d_old, self.d_new) == ("o", "ja"):
            stem = stem[:-1]

        # Для гетероклитик на -ин- во мн. ч.
        if (self.d_old, self.d_new) == ("o", "en") and not stem.endswith(("АР", "ТЕЛ")):
            stem += "ИН"

        return stem

    def _check_grd(self, stem):
        if not self.prop:
            return stem, None

        grd = None
        match = re.search("(ГРАД|ГОРОД)$", stem)

        if match:
            stem, grd = stem[: match.start()], match.group()

        return stem, grd

    def check_reduction_markup(self, stem):
        nb_lite = (
            self.nb.replace("+о", "")
            .replace("+е", "")
            .replace("-о", "")
            .replace("-е", "")
        )

        if "+" in nb_lite:
            stem += nb_lite[nb_lite.index("+") + 1 :].upper()
        elif "-" in nb_lite:
            stem = stem[: -len(nb_lite[nb_lite.index("-") + 1 :])]

        return stem

    def get_infl(self, stem):
        if not self.pt:
            if self.d_old == "a":
                return "А"
            if self.d_old == "ja":
                return "А" if stem.endswith(letters.cons_hush) else "Я"
            if self.d_old == "o":
                return "Ъ" if self.gen == "м" else "О"
            if self.d_old == "jo":
                if self.gen == "м":
                    return (
                        "Ь"
                        if stem.endswith(letters.cons_soft + letters.cons_hush)
                        else "И"
                    )
                return "Е"
            if self.d_old == "u":
                return "Ъ"
            if self.d_old == "i":
                return "Ь"
            if self.d_old == "en":
                return "Ь"
            if self.d_old == "men":
                return "Я"
            if self.d_old == "ent":
                return "А" if stem.endswith(letters.cons_hush) else "Я"
            if self.d_old == "er":
                return "И"
            if self.d_old == "es":
                return "О"
            return "Ь"
        else:
            if self.d_old == "a":
                return "Ы"
            if self.d_old == "o":
                return "А"
            if self.gen == "м":
                return "ИЕ"
            return "И"

    @property
    def lemma(self) -> str:
        # Проверка на исключительность
        for key in utils.spec.noun:
            if re.match(key, self.reg):
                return utils.spec.noun[key]

        # Стемминг (с учётом особого смешения)
        if self.d_new in ("a", "ja", "i") and self.gen == "ср":
            stem = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, "м"), utils.infl.noun
            )
        else:
            stem = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, self.gen), utils.infl.noun
            )

        if stem is None:
            return "None"

        # Проверка на склоняемость второй части
        stem, grd = self._check_grd(stem)
        if grd is not None:
            stem = self.get_stem(
                stem, (self.d_new, self.case, self.num, self.gen), utils.infl.noun
            )

        # Обработка основы
        if stem is None:
            return "None"

        # Модификации по типам склонения и другие
        stem = self._decl_spec_modif(stem)

        # Первая палатализация
        if stem[-1] in "ЧЖШ" and (
            (self.case, self.num, self.gen) == ("зв", "ед", "м") or stem in ("ОЧ", "УШ")
        ):
            if (self.d_old, self.d_new) == ("jo", "o"):
                stem = stem[:-1] + letters.palat_1_jo[stem[-1]]
            else:
                stem = stem[:-1] + letters.palat_1[stem[-1]]

        # Вторая палатализация
        elif "*" in self.nb and stem[-1] in "ЦЗСТ":
            stem = stem[:-1] + letters.palat_2[stem[-1]]

        # Прояснение/исчезновение редуцированных
        if any(tag in self.nb for tag in ("+о", "+е", "-о", "-е")):
            stem = self._de_reduce_manual(stem)
        elif stem[-1] == "Ц" and self._is_reduced():
            stem = self._de_reduce_auto(stem)

        # 'НОВЪ' --> 'НОВГОРОДЪ'; 'ЦАРЬ' --> 'ЦАРГРАДЪ' (?)
        if grd is not None:
            stem += grd

        # Возвращение маркера одушевлённости
        if self.prop:
            stem = "*" + stem
            stem = "*" + stem

        # Нахождение флексии
        return stem + self.get_infl(stem)

    @property
    def pickled(self):
        return [self.pos, self.d_old, self.case, self.num, self.gen]
