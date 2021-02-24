import re

import utils.infl
from utils import letters
from .noun import Noun


class Adjective(Noun):
    def _de_comp_suffix(self, stem):
        if (self.case, self.num, self.gen) in (("им", "ед", "м"), ("им", "ед", "ср")):
            return stem

        suffix = re.search("[ИЪЬ]?Ш$", stem)
        if suffix:
            stem = stem[: -len(suffix.group())]
        return stem

    def get_infl(self, stem):
        if self.d_old in ("a", "o", "тв"):
            return "ИИ" if stem.endswith(letters.cons_palat) else "ЫИ"
        return "И" if stem.endswith(letters.vows) else "ИИ"

    @property
    def lemma(self) -> str:
        # Стемминг
        stem = self.get_stem(
            self.reg,
            (self.d_new, self.case, self.num, self.gen),
            utils.infl.noun if self.d_old not in ("м", "тв") else utils.infl.pronoun,
        )

        if stem is None:
            return "None"

        # Суффиксы сравнительной степени
        if self.pos == "прил/ср":
            stem = self._de_comp_suffix(stem)

        # Плюс-минус
        stem = self.check_reduction_markup(stem)

        # Вторая палатализация
        if "*" in self.nb and stem[-1] in "ЦЗСТ":
            stem = stem[:-1] + letters.palat_2[stem[-1]]

        # Удаление прояснённых редуцированных
        if "-о" in self.nb or "-е" in self.nb:
            stem = stem[:-2] + stem[-1]

        # Возвращение маркера одушевлённости
        if self.prop:
            stem = "*" + stem

        if stem.endswith("#"):
            stem = stem.rstrip("#") + "-"

        # Нахождение флексии
        if self.prop and self.d_old not in ("м", "тв"):
            return stem + super().get_infl(stem)
        return stem + self.get_infl(stem)
