import functools
import re


def skip_chars(string, start):
    if string[start] == "<":
        start += len(re.search(r"(<.+?>)", string[start:]).group(1))
    elif string[start] == "&":
        start += len(re.search(r"(&.+?;)", string[start:]).group(1)) - 1

    if string[start] in "<&":
        start = skip_chars(string, start)

    return start


def count_chars(string, num=-1):
    if num > -1:
        res = skip_chars(string, 0)

        for _ in range(num):
            res += 1
            res = skip_chars(string, res)

        return res

    string = re.sub(r"<.+?>", "", string)
    string = re.sub(r"&.+?;", "S", string)

    return len(string)


def replace_chars(string, fr, to):
    assert len(fr) == len(to)
    return "".join([dict(zip(fr, to)).get(c, c) for c in string])


def replace_overline_chars(match):
    res = replace_chars(
        match.group(1).upper(),
        "БВГДЖЗКЛМНОПРСТХЦЧШЩFАЕD+ЮRGЯИIЪЬWЫУU",
        (
            "ⷠ",
            "ⷡ",
            "ⷢ",
            "ⷣ",
            "ⷤ",
            "ⷥ",
            "ⷦ",
            "ⷧ",
            "ⷨ",
            "ⷩ",
            "ⷪ",
            "ⷫ",
            "ⷬ",
            "ⷭ",
            "ⷮ",
            "ⷯ",
            "ⷰ",
            "ⷱ",
            "ⷲ",
            "ⷳ",
            "ⷴ",
            "ⷶ",
            "ⷷ",
            "ⷹ",
            "ⷺ",
            "ⷻ",
            "ⷽ",
            "ⷾ",
            "ⷼ",
            "ꙶ",
            "ꙵ",
            "ꙸ",
            "ꙺ",
            "ꙻ",
            "ꙹ",
            "ꙷ",
            "ⷪꙷ",  # Здесь два символа
        ),
    )
    return "҇" + res if match.group(1).islower() else res


def skip_none(fun):
    @functools.wraps(fun)
    def wrapped(*args, **kwargs):
        if args[1] is None:
            return "None"
        return fun(*args, **kwargs)

    return wrapped
