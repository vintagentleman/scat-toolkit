import json
import shelve
from pathlib import Path

import click
import xlsxwriter

from components.normalizer.normalizer import Normalizer
from models.row import WordRow

__root__ = Path(__file__).resolve().parents[1]


class Annotator:
    def __init__(self, text, pickle):
        self.text = Path.joinpath(__root__, "generated", "tokenizer", text)

        self.pickle = shelve.open(
            str(Path.joinpath(__root__, "generated", "converter", "pkl", pickle))
        )

        self.clusters = json.load(
            Path.joinpath(__root__, "resources", "tagset_clusters.json").open(
                encoding="utf-8"
            )
        )

        self.workbook = xlsxwriter.Workbook(
            str(
                Path.joinpath(
                    __root__, "generated", "annotator", f"{self.text.stem}.xlsx"
                )
            )
        )

        self.styles = {
            "ambiguous": self.workbook.add_format({"bg_color": "yellow"}),
            "correct": self.workbook.add_format({"bg_color": "lime"}),
        }

    def _transform_tagsets_using_clusters(self, norm):
        tagsets = self.pickle[norm]
        copy = tagsets[:]

        for i, tagset in enumerate(copy):
            # Пропускаем неизменяемые ЧР
            if len(tagset) == 1:
                continue

            pos = tagset[0]
            # У глаголов пропускаем для сопоставления колонки с наклонением и временем
            if pos == "гл":
                subtagset = tagset[3:5]
            # У причастий пропускаем только время
            elif pos == "прич":
                subtagset = [tagset[1]] + tagset[3:]
            # У прочих только ЧР
            else:
                subtagset = tagset[1:]

            for cluster in self.clusters:
                if subtagset in cluster:
                    # Восстанавливаем пропущенные колонки
                    if pos == "гл":
                        tagsets += [
                            tagset[:3] + list_ + [tagset[5]] for list_ in cluster
                        ]
                    elif pos == "прич":
                        tagsets += [
                            [pos, list_[0], tagset[2]] + list_[1:] for list_ in cluster
                        ]
                    else:
                        tagsets += [[pos] + list_ for list_ in cluster]

                    del tagsets[i]
                    break

        # Добавляем пустые колонки в конец
        return [tagset + [""] * (6 - len(tagset)) for tagset in tagsets]

    def _write_row(self, sheet, i: int, line: tuple) -> bool:
        if not all(len(cell) == 0 for cell in line[1:]):
            # Если колонок больше одной, то это цифирь
            sheet.write(i, 0, line[0], self.styles["correct"])
            sheet.write(i, 1, line[1])
            return False

        sheet.write(i, 0, line[0])

        if line[0].startswith("<"):  # Skip XML words
            return False

        parsed = WordRow(self.text.stem, list(map(str.strip, line))).parsed_word

        if parsed is None:  # Skip non-word rows
            return False

        norm = Normalizer.normalize(parsed)

        if norm not in self.pickle:  # Skip words whose norm isn't in the shelf
            return False

        tagsets = self._transform_tagsets_using_clusters(norm)

        # Если разбор один, то помечаем его и не учитываем при подсчёте
        if len(tagsets) == 1:
            sheet.write(
                i,
                0,
                line[0],
                self.styles["correct"] if tagsets[0][0] != "гл" else None,
            )
            sheet.write_row(i, 1, tagsets[0])
            return True

        # Если нет, то выделяем неоднозначные позиции
        for j, col in enumerate(zip(*tagsets), start=1):
            # Если конфликтов нет, то просто записываем
            if col.count(col[0]) == len(col):
                sheet.write(i, j, col[0])
            # Конфликты выделяем и отображаем все опции
            else:
                sheet.write_blank(i, j, None, self.styles["ambiguous"])
                sheet.data_validation(
                    i,
                    j,
                    i,
                    j,
                    {
                        "validate": "list",
                        "source": list(dict.fromkeys(col)),
                        "show_error": False,
                    },
                )
        return False

    def run(self, students: int, workload: int, offset: int):
        with open(self.text, "r") as f:
            lines = f.readlines()[offset:]
            lines = (tuple(map(str.strip, line.split("\t"))) for line in lines)

        for student in range(students):
            sheet = self.workbook.add_worksheet()
            sheet.set_column("A:A", 40)
            limit = workload

            for i, line in enumerate(lines):
                if self._write_row(sheet, i, line):
                    limit += 1

                if i + 1 == limit:
                    break

        self.workbook.close()


@click.command()
@click.argument("text", type=click.Path())  # Relative to generated/tokenizer
@click.argument("pickle", type=click.Path())  # Relative to generated/converter/pkl
@click.option("--students", default=10)
@click.option("--workload", default=250)
@click.option("--offset", default=0)
def main(text: str, pickle: str, students: int, workload: int, offset: int):
    Path.joinpath(__root__, "generated").mkdir(exist_ok=True)
    Path.joinpath(__root__, "generated", "annotator").mkdir(exist_ok=True)
    Annotator(text, pickle).run(students, workload, offset)


if __name__ == "__main__":
    main()
