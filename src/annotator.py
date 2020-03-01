import shelve
from pathlib import Path

from fire import Fire
import pandas as pd
import xlsxwriter

from src import __root__
from models import Row, Word


class Annotator:
    def __init__(self, db, inp="raw/*.tsv"):
        self.db = shelve.open(str(Path.joinpath(__root__, "out", db)))
        self.inp = Path.joinpath(__root__, "inp").glob(inp)

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
                        form = Word(filename.stem, i, line.word, line.ana).reg

                        if form in self.db:
                            # Если разбор один, то помечаем его и не учитываем при подсчёте
                            if len(self.db[form]) == 1:
                                sheet.write(i, 0, row[0], correct)
                                sheet.write_row(i, 1, self.db[form][0])
                                limit += 1
                            # Если нет, то выделяем неоднозначные позиции
                            else:
                                msd = zip(*self.db[form])

                                for j, col in enumerate(msd, start=1):
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
