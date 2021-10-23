import re

from utils import replace_chars


class UnicodeConverter:
    INLINE_ASCII = "IRVWU+FSGDLQЯ$"
    INLINE_UNICODE = "їѧѵѡѹѣѳѕѫꙋѯѱꙗ҂"

    OVERLINE_ASCII = "БВГДЖЗКЛМНОПРСТХЦЧШЩFАЕD+ЮRGЯИIЪЬWЫУU"
    OVERLINE_UNICODE = (
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
        "ⷪꙷ",  # This is two characters
    )

    @classmethod
    def __skip_chars(cls, text: str, start: int) -> int:
        if text[start] == "<":
            start += len(re.search(r"(<.+?>)", text[start:]).group(1))
        elif text[start] == "&":
            start += len(re.search(r"(&.+?;)", text[start:]).group(1)) - 1

        if text[start] in "<&":
            start = cls.__skip_chars(text, start)

        return start

    @classmethod
    def __count_chars(cls, text: str, number: int = -1) -> int:
        if number > -1:
            res = cls.__skip_chars(text, 0)

            for _ in range(number):
                res += 1
                res = cls.__skip_chars(text, res)

            return res

        text = re.sub(r"<.+?>", "", text)
        text = re.sub(r"&.+?;", "S", text)

        return len(text)

    @classmethod
    def __replace_overline_chars(cls, match: re.Match) -> str:
        """
        Overline character replacer function.
        :param match: Match object for characters in parentheses
        :return: Unicode replacement string, with or without the titlo character
        """
        text = replace_chars(
            match.group(1).upper(), cls.OVERLINE_ASCII, cls.OVERLINE_UNICODE
        )
        return "҇" + text if match.group(1).islower() else text

    @classmethod
    def convert(cls, text: str) -> str:
        text = re.sub(r"\((.+?)\)", cls.__replace_overline_chars, text)
        text = replace_chars(text, cls.INLINE_ASCII, cls.INLINE_UNICODE)

        if "#" in text:
            text = text.replace("#", "")
            number = int(cls.__count_chars(text) > 1)
            text = (
                text[: cls.__count_chars(text, number) + 1]
                + "҃"
                + text[cls.__count_chars(text, number) + 1 :]
            )

        return text.replace("ѡⷮ", "ѿ").lower()
