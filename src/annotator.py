import json
import shelve
from pathlib import Path

from fire import Fire
import pandas as pd
import xlsxwriter

from src import __root__
from models import Row, Word


class Annotator:
    def __init__(self, db="db", inp="*.tsv"):
        self.db = shelve.open(str(Path.joinpath(__root__, "out", db)))
        self.inp = Path.joinpath(__root__, "inp", "raw").glob(inp)

        self.tagsets = json.load(
            Path.joinpath(__root__, "src", "utils", "tagsets.json").open(encoding="utf-8")
        )

    def run(self, students=10, workload=250, offset=0):
        for filename in self.inp:
            df = pd.read_csv(filename, sep="\t", header=None, na_filter=False)
            book = xlsxwriter.Workbook(
                str(Path.joinpath(__root__, "out", f"{filename.stem}.xlsx"))
            )

            # Форматирование
            ambiguous = book.add_format({"bg_color": "yellow"})
            correct = book.add_format({"bg_color": "lime"})
            student = 0

            while student < students:
                sheet = book.add_worksheet()
                sheet.set_column("A:A", 40)
                limit = workload

                for i, row in df.iloc[offset:].iterrows():
                    if all(len(cell) == 0 for cell in row[1:]):
                        sheet.write(i, 0, row[0])
                        line = Row(row.map(str.strip).to_list())
                        word = Word(filename.stem, i, line.word, line.ana)
                        form = word.reg

                        if form in self.db:
                            msd = self.db[form]

                            for cluster in self.tagsets:
                                if len(set(map(tuple, msd)) & set(map(tuple, cluster))):
                                    msd = cluster

                            # Если разбор один, то помечаем его и не учитываем при подсчёте
                            if len(msd) == 1:
                                sheet.write(i, 0, row[0], correct)
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
                        student += 1
                        break

            book.close()


if __name__ == "__main__":
    Fire(Annotator)
