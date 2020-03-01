import re
from utils import lib, letters
from . import Lemmatizer


class NounLemmatizer(Lemmatizer):
    def __init__(self, w):
        super().__init__(w)

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
        if "/" in w.msd[0] and w.msd[0] != "р/скл":
            self.d_old, self.d_new = w.msd[0].split("/")
        else:
            self.d_old = self.d_new = w.msd[0]

        self.case = w.msd[1].split("/")[-1]

        # Pluralia tantum
        self.pt = w.msd[2] == "pt"
        if self.pt:
            self.num = "мн"
        else:
            self.num = w.msd[2].split("/")[-1] if w.msd[2] != "0" else "ед"

        self.gen = w.msd[3].split("/")[-1] if w.msd[3] != "0" else "м"
        self.nb = w.msd[4]

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
        for th in lib.them_suff:
            if th in (self.d_old, self.d_new):
                suffix = re.search(lib.them_suff[th], stem)
                if suffix:
                    stem = stem[: -len(suffix.group())]

        return stem

    def __add_suffix(self, stem):
        if self.d_old == "en" and not (
            stem.endswith("ЕН") or re.match("Д[ЪЬ]?Н", stem)
        ):
            suffix = re.search(lib.them_suff[self.d_old], stem)
            if suffix:
                stem = stem[: -len(suffix.group())]
            stem += "ЕН"

        elif self.d_old == "uu" and not stem.endswith("ОВ"):
            suffix = re.search(lib.them_suff[self.d_old], stem)
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

    def get_lemma(self):
        # Проверка на исключительность
        for key in lib.noun_spec:
            if re.match(key, self.reg):
                return self.reg, lib.noun_spec[key][0] + lib.noun_spec[key][1]

        # Стемминг (с учётом особого смешения)
        if self.d_new in ("a", "ja", "i") and self.gen == "ср":
            s_old = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, "м"), lib.nom_infl
            )
        else:
            s_old = self.get_stem(
                self.reg, (self.d_new, self.case, self.num, self.gen), lib.nom_infl
            )

        if s_old is None:
            return self.reg, None

        # Проверка на склоняемость второй части
        s_new, grd = self._check_grd(s_old)
        if grd is not None:
            s_new = self.get_stem(
                s_new, (self.d_new, self.case, self.num, self.gen), lib.nom_infl
            )

        # Обработка основы
        if s_new is None:
            return self.reg, None

        # Модификации по типам склонения и другие
        s_new = self._decl_spec_modif(s_new)

        # Первая палатализация
        if s_new[-1] in "ЧЖШ" and (
            (self.case, self.num, self.gen) == ("зв", "ед", "м")
            or s_new in ("ОЧ", "УШ")
        ):
            if (self.d_old, self.d_new) == ("jo", "o"):
                s_new = s_new[:-1] + letters.palat_1_jo[s_new[-1]]
            else:
                s_new = s_new[:-1] + letters.palat_1[s_new[-1]]

        # Вторая палатализация
        elif "*" in self.nb and s_new[-1] in "ЦЗСТ":
            s_new = s_new[:-1] + letters.palat_2[s_new[-1]]

        # Прояснение/исчезновение редуцированных
        if any(tag in self.nb for tag in ("+о", "+е", "-о", "-е")):
            s_new = self._de_reduce_manual(s_new)
        elif s_new[-1] == "Ц" and self._is_reduced():
            s_new = self._de_reduce_auto(s_new)

        # 'НОВЪ' --> 'НОВГОРОДЪ'; 'ЦАРЬ' --> 'ЦАРГРАДЪ' (?)
        if grd is not None:
            s_new += grd

        # Возвращение маркера одушевлённости
        if self.prop:
            s_old = "*" + s_old
            s_new = "*" + s_new

        # Нахождение флексии
        return s_old, s_new + self.get_infl(s_new)
