import csv
import sqlite3

from pathlib import Path
from contextlib import closing


SQLITE_COLUMNS = {
    "input_author_name": "TEXT",
    "openlibrary_key": "TEXT",
    "matched_author_name": "TEXT",
    "match_score": "REAL",
    "score_gap": "REAL",
    "candidate_count": "INTEGER",
    "confidence_level": "TEXT",
    "enrichment_status": "TEXT",
    "birth_date": "TEXT",
    "death_date": "TEXT",
    "bio": "TEXT",
    "source": "TEXT"
}


def write_csv(rows: list[dict], output_path: Path) -> None:
    """
    Write the provided rows to a CSV file.
    :param rows: List of rows to write.
    :param output_path: Path where the CSV file will be created.
    :return: None.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        output_path.write_text("", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def normalize_sqlite_value(value: object) -> object:
    """
    Normalize a value before inserting it into SQLite.
    :param value: Value to normalize.
    :return: Normalized value compatible with SQLite.
    """
    if isinstance(value, bool):
        return int(value)

    if value == "":
        return None

    return value


def write_sqlite_db(rows: list[dict], output_path: Path, table_name: str = "authors_enriched") -> None:
    """
    Write the provided rows to a SQLite database table.
    :param rows: List of rows to insert.
    :param output_path: Path where the SQLite database will be created.
    :param table_name: Name of the destination table.
    :return: None.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(output_path)) as connection:
        cursor = connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        column_definitions = ", ".join(
            f"{column} {column_type}"
            for column, column_type in SQLITE_COLUMNS.items()
        )
        cursor.execute(f"CREATE TABLE {table_name} ({column_definitions})")

        if not rows:
            return

        columns = list(SQLITE_COLUMNS.keys())
        placeholders = ", ".join("?" for _ in columns)
        column_names = ", ".join(columns)

        values = [
            tuple(normalize_sqlite_value(row.get(column)) for column in columns)
            for row in rows
        ]

        cursor.executemany(
            f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})",
            values,
        )
        connection.commit()
