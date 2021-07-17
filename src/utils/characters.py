latin_uppercase_homoglyphs = "ABEKMHOPCTX"
latin_lowercase_homoglyphs = "aeopcyx"

cyrillic_uppercase_homoglyphs = "АВЕКМНОРСТХ"
cyrillic_lowercase_homoglyphs = "аеорсух"

latin_homoglyphs = latin_uppercase_homoglyphs + latin_lowercase_homoglyphs
cyrillic_homoglyphs = cyrillic_uppercase_homoglyphs + cyrillic_lowercase_homoglyphs

latin_special_characters = "SIWDGUFRLQ"
cyrillic_special_characters = ("З", "И", "О", "У", "У", "У", "Ф", "Я", "КС", "ПС")

vowels = ("+", "А", "Е", "И", "О", "У", "Ъ", "Ы", "Ь", "Ю", "Я")
consonants = (
    "Б",
    "В",
    "Г",
    "Д",
    "Ж",
    "З",
    "К",
    "Л",
    "М",
    "Н",
    "П",
    "Р",
    "С",
    "Т",
    "Ф",
    "Х",
    "Ц",
    "Ч",
    "Ш",
    "Щ",
)

soft_consonants = ("З", "Л", "Н", "Р", "С")
hush_consonants = ("Ж", "ЖД", "Ц", "Ч", "Ш", "ШТ", "Щ")
sonorant_consonants = ("Л", "М", "Н", "Р")
palatalized_consonants = ("К", "Г", "Х")

palatalization_1 = {"Ч": "К", "Ж": "Г", "Ш": "Х"}
soft_palatalization_1 = {"Ч": "Ц", "Ж": "З", "Ш": "С"}
palatalization_2 = {"Ц": "К", "З": "Г", "С": "Х", "Т": "К"}
