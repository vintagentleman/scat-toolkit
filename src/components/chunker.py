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
    def __is_followed_by_i_after_strongish_punctuation(row: Row, next_row: Row) -> bool:
        return (
            row.tail_punctuation is not None
            and set(row.tail_punctuation.source) & {".", ":", ";"}
            and next_row.word is not None
            and next_row.word.lemma == "и"
        )

    @staticmethod
    def __is_followed_by_relative_conjunction_after_punctuation(
        row: Row, next_row: Row
    ) -> bool:
        return (
            row.tail_punctuation is not None
            and next_row.word is not None
            and next_row.word.lemma in ("иже", "еже")
        )

    @staticmethod
    def __is_followed_by_punctuation_and_imperative(row: Row, next_row: Row) -> bool:
        return (
            row.tail_punctuation is not None
            and next_row.word is not None
            and next_row.word.tagset is not None
            and next_row.word.pos.startswith("гл")
            and next_row.word.tagset.mood == "повел"
        )

    @classmethod
    def chunk(cls, rows: List[Row]) -> List[List[Row]]:
        chunks = []
        chunk = []

        for i, row in enumerate(rows):
            chunk.append(row)

            if cls.__has_strong_punctuation(row) or (
                i < len(rows) - 1
                and (
                    cls.__is_followed_by_i_after_strongish_punctuation(row, rows[i + 1])
                    or cls.__is_followed_by_relative_conjunction_after_punctuation(
                        row, rows[i + 1]
                    )
                    or cls.__is_followed_by_punctuation_and_imperative(row, rows[i + 1])
                )
            ):
                chunks.append(chunk)
                chunk = []

        return chunks
