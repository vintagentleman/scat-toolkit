import json
import shelve
from pathlib import Path

from fire import Fire
import pandas as pd
import xlsxwriter

from src import __root__
from models import Row, Word


class Annotator:
    def __init__(self, db="db", filename="AKush.tsv"):
        self.db = shelve.open(str(Path.joinpath(__root__, "out", db)))
        self.filename = Path.joinpath(__root__, "inp", "raw", filename)

        self.clusters = json.load(
            Path.joinpath(__root__, "src", "utils", "clusters.json").open(
                encoding="utf-8"
            )
        )

    def get_msd(self, form):
        tagsets = self.db[form]
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
                        tagsets += [tagset[:3] + list_ + tagset[5] for list_ in cluster]
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

    def run(self, students=10, workload=250, offset=0):
        df = pd.read_csv(self.filename, sep="\t", header=None, na_filter=False)
        rows = df.iloc[offset:].itertuples(index=False, name=None)
        book = xlsxwriter.Workbook(
            str(Path.joinpath(__root__, "out", f"{self.filename.stem}.xlsx"))
        )

        # Форматирование
        ambiguous = book.add_format({"bg_color": "yellow"})
        correct = book.add_format({"bg_color": "lime"})

        for student in range(students):
            sheet = book.add_worksheet()
            sheet.set_column("A:A", 40)
            limit = workload

            for i, row in enumerate(rows):
                if all(len(cell) == 0 for cell in row[1:]):
                    sheet.write(i, 0, row[0])
                    line = Row(list(map(str.strip, row)))
                    word = Word(self.filename.stem, i, line.word, line.ana)
                    form = word.reg

                    if form in self.db:
                        msd = self.get_msd(form)

                        # Если разбор один, то помечаем его и не учитываем при подсчёте
                        if len(msd) == 1:
                            sheet.write(
                                i, 0, row[0], correct if msd[0][0] != "гл" else None
                            )
                            sheet.write_row(i, 1, msd[0])
                            limit += 1
                        # Если нет, то выделяем неоднозначные позиции
                        else:
                            for j, col in enumerate(zip(*msd), start=1):
                                # Если конфликтов нет, то просто записываем
                                if col.count(col[0]) == len(col):
                                    sheet.write(i, j, col[0])
                                # Конфликты выделяем и отображаем все опции
                                else:
                                    sheet.write_blank(i, j, None, ambiguous)
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
                # Если колонок больше одной, то это цифирь
                else:
                    sheet.write(i, 0, row[0], correct)
                    sheet.write(i, 1, row[1])

                if i == limit:
                    break

        book.close()


if __name__ == "__main__":
    Fire(Annotator)
