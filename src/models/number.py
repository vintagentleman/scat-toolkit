class Number:
    NUMBER_MAP = {
        "А": 1,
        "A": 1,  # Latin
        "В": 2,
        "B": 2,  # Latin
        "Г": 3,
        "Д": 4,
        "Е": 5,
        "E": 5,  # Latin
        "S": 6,
        "З": 7,
        "И": 8,
        "I": 10,
        "К": 20,
        "K": 20,  # Latin
        "Л": 30,
        "М": 40,
        "M": 40,  # Latin
        "Н": 50,
        "H": 50,  # Latin
        "О": 70,
        "O": 70,  # Latin
        "П": 80,
        "Р": 100,
        "P": 100,  # Latin
        "С": 200,
        "C": 200,  # Latin
        "Т": 300,
        "T": 300,  # Latin
        "U": 400,
        "D": 400,
        "Ф": 500,
        "Х": 600,
        "X": 600,  # Latin
        "W": 800,
        "Ц": 900,
        "Ч": 90,
        "R": 900,
        "L": 60,
        "Q": 700,
        "F": 9,
        "V": 400,
    }

    def __init__(self, text):
        self.text = (
            text + "#" if "#" not in text else text
        )  # Append an obligatory titlo if it is missing
        self.number, self.suffix = (
            self.text.split("#", 1) if "#" in self.text else (self.text, str())
        )

        if self.number.startswith("$"):
            self.value = self.NUMBER_MAP[
                self.number[1]
            ] * 1000 + sum(  # The first number is a thousand digit
                self.NUMBER_MAP.get(letter, 0) for letter in self.number[2:]
            )
        else:
            self.value = sum(self.NUMBER_MAP.get(letter, 0) for letter in self.number)

    def __str__(self):
        return f"{self.value}-{self.suffix}" if self.suffix else str(self.value)
