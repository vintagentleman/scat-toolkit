noun = {
    "И([ИС]|ИСУС)[ЪЬ`]?$": ("*ИИСУС", "Ъ"),
    "ПОЛ.*Д[ЕЬ]?Н": ("ПОЛДЕН", "Ь"),
    "ПОЛ.*НОЧ": ("ПОЛНОЧ", "Ь"),
    "ПОЛ.*НОЩ": ("ПОЛНОЩ", "Ь"),
}

noun_them_suff = {
    "en": "[ЪЬ]?Н$",
    "men": "([ЕЯ]|[ЪЬ]?)Н$",
    "ent": "[АЯ]Т$",
    "es": "(Е|[ЪЬ]?)С$",
    "er": "(Е|[ЪЬ]?)Р$",
    "uu": "[ЪЬ]?В$",
}

pronoun = {
    "": "И",
    "ВАШ": "Ь",
    "ВЕС": "Ь",
    "ЕЛИК": "О",
    "М": "ОИ",
    "НАШ": "Ь",
    "ОН": "Ъ",
    "ОНСИЦ": "А",
    "САМ": "Ъ",
    "СВ": "ОИ",
    "СИЦ": "Ь",
    "Т": "ОИ",
    "ТВ": "ОИ",
}

numeral = {
    "ЕДИН.*НАДЕСЯТ": "ЕДИННАДЕСЯТЕ",
    "Д[ЪЬ]?В.*НАДЕСЯТ": "ДВАНАДЕСЯТЕ",
    "ТР.*НАДЕСЯТ": "ТРИНАДЕСЯТЕ",
    "ЧЕТЫР.*НАДЕСЯТ": "ЧЕТЫРЕНАДЕСЯТЕ",
    "ПЯТ.*НАДЕСЯТ": "ПЯТЬНАДЕСЯТЕ",
    "ШЕСТ.*НАДЕСЯТ": "ШЕСТЬНАДЕСЯТЕ",
    "СЕДМ.*НАДЕСЯТ": "СЕДМЬНАДЕСЯТЕ",
    "ОСМ.*НАДЕСЯТ": "ОСМЬНАДЕСЯТЕ",
    "ДЕВЯТ.*НАДЕСЯТ": "ДЕВЯТЬНАДЕСЯТЕ",
    "Д[ЪЬ]?В.*ДЕСЯТ": "ДВАДЕСЯТИ",
    "ТР.*ДЕСЯТ": "ТРИДЕСЯТЕ",
    "ЧЕТЫР.*ДЕСЯТ": "ЧЕТЫРЕДЕСЯТЕ",
    "ПЯТ.*ДЕСЯТ": "ПЯТЬДЕСЯТЪ",
    "ШЕСТ.*ДЕСЯТ": "ШЕСТЬДЕСЯТЪ",
    "СЕДМ.*ДЕСЯТ": "СЕДМЬДЕСЯТЪ",
    "ОСМ.*ДЕСЯТ": "ОСМЬДЕСЯТЪ",
    "ДЕВЯТ.*ДЕСЯТ": "ДЕВЯТЬДЕСЯТЪ",
    "Д[ЪЬ]?В.*С[ЪО]?Т": "ДВ+СТ+",
    "ТР.*С[ЪО]?Т": "ТРИСТА",
    "ЧЕТЫР.*С[ЪО]?Т": "ЧЕТЫРЕСТА",
    "ПЯТ.*С[ЪО]?Т": "ПЯТЬСОТЪ",
    "ШЕСТ.*С[ЪО]?Т": "ШЕСТЬСОТЪ",
    "СЕДМ.*С[ЪО]?Т": "СЕДМЬСОТЪ",
    "ОСМ.*С[ЪО]?Т": "ОСМЬСОТЪ",
    "ДЕВЯТ.*С[ЪО]?Т": "ДЕВЯТЬСОТЪ",
}

part_el = {
    "(.[ЪЬ]?)ШЕ$": "ОИ",
    "(.*)ШЕ$": "И",
}

part = {
    "(.*)[ЕИ][МН]$": "Я",
    "(.[ЪЬ]?)Ш[+Е]Д$": "ОИ",
    "(.*)Ш[+Е]Д$": "И",
}

imperfect = {
    "(.*)ЖИВ$": "ЖИ",
    "()ИД$": "И",
    "(.*)ЯД$": "ЯС",
    "()Б$": "БЫ",
}

prep = {
    "(.+)С[ЪЬ]$": "\\1ЗЪ",
    "Г[ЪЬ]$": "КЪ",
    "З[ЪЬ]$": "СЪ",
    "ОБ[ЪЬ]$": "О",
}

prep_var = (
    "БЕЗО",
    "ВО",
    "ИЗО",
    "КО",
    "НАДО",
    "ОБО",
    "ОТО",
    "ПЕРЕДО",
    "ПОДО",
    "ПРЕДО",
    "ПРОТИВУ",
    "СО",
    "СУПРОТИВУ",
)
