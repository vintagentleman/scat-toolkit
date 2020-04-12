import re
from utils import lib, letters
from .noun import NounLemmatizer


class AdjectiveLemmatizer(NounLemmatizer):
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

    def get_lemma(self):
        # Стемминг
        s_old = self.get_stem(
            self.reg,
            (self.d_new, self.case, self.num, self.gen),
            lib.nom_infl if self.d_old not in ("м", "тв") else lib.pron_infl,
        )

        if s_old is None:
            return self.reg, None

        s_new = s_old

        # Суффиксы сравнительной степени
        if self.pos == "прил/ср":
            s_new = self._de_comp_suffix(s_new)

        # Плюс-минус
        s_new = self.check_reduction_markup(s_new)

        # Вторая палатализация
        if "*" in self.nb and s_new[-1] in "ЦЗСТ":
            s_new = s_new[:-1] + letters.palat_2[s_new[-1]]

        # Удаление прояснённых редуцированных
        if "-о" in self.nb or "-е" in self.nb:
            s_new = s_new[:-2] + s_new[-1]

        # Возвращение маркера одушевлённости
        if self.prop:
            s_old = "*" + s_old
            s_new = "*" + s_new

        # Нахождение флексии
        if self.prop and self.d_old not in ("м", "тв"):
            return s_old, s_new + super().get_infl(s_new)
        return s_old, s_new + self.get_infl(s_new)
