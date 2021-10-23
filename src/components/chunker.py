from typing import List

from models.row import Row


class Chunker:
    @staticmethod
    def __has_strong_punctuation(row: Row) -> bool:
        return row.tail_punctuation is not None and set(row.tail_punctuation.source) & {
            ":",
            ";",
        }

    @staticmethod
    def __has_punctuation_before_conjunction(row: Row, next_row: Row) -> bool:
        return (
            row.tail_punctuation is not None
            and set(row.tail_punctuation.source) & {".", ":", ";"}
            and next_row.word is not None
            and next_row.word.lemma in ("И", "ИЖЕ")
        )

    @classmethod
    def chunk(cls, rows: List[Row]) -> List[List[Row]]:
        chunks = []
        chunk = []

        for i, row in enumerate(rows):
            chunk.append(row)

            if cls.__has_strong_punctuation(row) or (
                i < len(rows) - 1
                and cls.__has_punctuation_before_conjunction(row, rows[i + 1])
            ):
                chunks.append(chunk)
                chunk = []

        return chunks
