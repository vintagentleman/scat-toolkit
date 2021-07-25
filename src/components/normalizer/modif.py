import re

from utils import characters
from . import lib


def real_len(w):
    """Подсчёт длины слова без титла"""

    if "#" in w:
        return len(w) - 1

    return len(w)


def repl(w, d, mode="search"):
    """Замена буквосочетания"""

    for coll in d:

        if mode == "match":
            if re.match(coll, w):
                w = re.sub(coll, d[coll], w, 1)

        else:
            if re.search(coll, w):
                w = re.sub(coll, d[coll], w)

    return w


def repl_var(w, p, d, mode="search"):
    """Замена неоднозначного буквосочетания"""

    for coll in d:

        if mode == "match":
            if re.match(coll, w):
                if p in d[coll]:
                    w = re.sub(coll, d[coll][p], w, 1)
                else:
                    w = re.sub(coll, d[coll][""], w, 1)

        else:
            if re.search(coll, w):
                if p in d[coll]:
                    w = re.sub(coll, d[coll][p], w)
                else:
                    w = re.sub(coll, d[coll][""], w)

    return w


def modif_titlo_on_start(w, p):
    """Замена буквосочетаний под титлом (только в начале слов)"""

    w = repl(w, lib.titlo_on_start, "match")

    # Случаи с неоднозначным раскрытием
    w = repl_var(w, p, lib.titlo_on_start_var, "match")

    return w


def modif_titlo(w):
    """Замена буквосочетаний под титлом (везде)"""
    return repl(w, lib.titlo)


def modif_abbr(w, p):
    """Замена буквосочетаний в сокращённых корнях без титла"""

    # Случаи с неоднозначным раскрытием (надстроки случаев с однозначным)
    w = repl_var(w, p, lib.abbr_var_super)

    w = repl(w, lib.abbr)

    # Случаи с неоднозначным раскрытием (подстроки случаев с однозначным)
    w = repl_var(w, p, lib.abbr_var_sub)

    return w


def modif_not_on_end(w):
    """Замены *не* на конце слов"""

    for coll in lib.not_on_end:
        mo = re.search(coll, w)

        if mo and mo.end() != real_len(w):
            w = re.sub(coll, lib.not_on_end[coll], w, 1)

    return w


def modif_varia(w):
    """Замена разных буквосочетаний вне зависимости от положения в слове"""
    return repl(w, lib.varia)


def modif_stv(w):
    """Замена -ств- и -ск-"""

    mo = re.search("[ЕЬ]С(ТВ|К)", w)

    if mo and mo.start() > 2:
        w = re.sub("[ЕЬ]С(ТВ|К)", "С\\1", w)

    mo = re.search("С(ТВ|К)", w)

    if mo and mo.start() > 2:
        if w[mo.start() - 1] in set(characters.hush_consonants) - {"Ц"}:
            w = w[: mo.start()] + "Е" + w[mo.start() :]
        elif w[mo.start() - 1] == "Л":
            w = w[: mo.start()] + "Ь" + w[mo.start() :]

    return w


def modif_mv(w):
    """Замена -мь- и -вь- только внутри слов"""

    mo = re.search("([МВ])Ь", w)

    if mo and mo.end() < real_len(w):
        if w[mo.end()] not in set(characters.vowels) - {"Ъ", "Ь"}:
            w = re.sub("([МВ])Ь", "\\1", w)

    return w


def modif_on_end(w, p):
    """Замена буквосочетаний на конце слов"""

    for coll in lib.on_end:
        mo = re.search(coll + "$", w)

        if mo and mo.end() == real_len(w):
            w = w[: mo.start()] + re.sub(coll, lib.on_end[coll], w[mo.start() :])

    for coll in lib.on_end_var:
        mo = re.search(coll + "$", w)

        if mo and mo.end() == real_len(w):
            if p in lib.on_end_var[coll]:
                w = w[: mo.start()] + re.sub(
                    coll, lib.on_end_var[coll][p], w[mo.start() :]
                )
            else:
                w = w[: mo.start()] + re.sub(
                    coll, lib.on_end_var[coll][""], w[mo.start() :]
                )

    return w


def modif_prep(w):
    """Замена вариантов предлогов"""

    if last := w[-1] in characters.consonants:
        w += "Ь" if last in characters.hush_consonants else "Ъ"

    if w in lib.prep_var:
        w = w[:-1] + "Ъ"

    for regex in lib.prep:
        if re.match(regex, w):
            w = re.sub(regex, lib.prep[regex], w)

    return w


def modif_errors(w):
    """Исправление ошибок"""

    w = repl(w, lib.errors)
    w = repl(w, lib.errors_on_start, "match")

    return w


def modif(wort, pos):
    wort_init = wort

    if "#" in wort:
        wort = modif_titlo_on_start(wort, pos)
        wort = modif_titlo(wort)

    if wort_init != wort:
        wort = wort[:-1]

    if "#" not in wort:
        wort = modif_abbr(wort, pos)

    wort = modif_not_on_end(wort)
    wort = modif_varia(wort)

    if not re.search("Ж[ЕЬ]?СК", wort):
        wort = modif_stv(wort)

    wort = modif_mv(wort)
    wort = modif_on_end(wort, pos)

    if pos == "пред":
        wort = modif_prep(wort)

    return modif_errors(wort)
