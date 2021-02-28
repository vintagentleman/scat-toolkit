class Number:
    NUMBER_MAP = {
        "А": 1,
        "В": 2,
        "Г": 3,
        "Д": 4,
        "Е": 5,
        "S": 6,
        "З": 7,
        "И": 8,
        "I": 10,
        "К": 20,
        "Л": 30,
        "М": 40,
        "Н": 50,
        "О": 70,
        "П": 80,
        "Р": 100,
        "С": 200,
        "Т": 300,
        "U": 400,
        "D": 400,
        "Ф": 500,
        "Х": 600,
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
