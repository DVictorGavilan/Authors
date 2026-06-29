import csv
import sqlite3

from src import load
from assertpy import assert_that
from contextlib import closing


def sample_rows() -> list[dict]:
    return [
        {
            "input_author_name": "Jane Austen",
            "openlibrary_key": "OL1A",
            "matched_author_name": "Jane Austen",
            "match_score": 0.99,
            "score_gap": 0.10,
            "candidate_count": 3,
            "confidence_level": "high_confidence",
            "enrichment_status": "enriched",
            "birth_date": "1775",
            "death_date": "",
            "bio": "English novelist",
            "source": "openlibrary",
        }
    ]


def test_write_csv_creates_file_with_rows(tmp_path):
    output_path = tmp_path / "output" / "authors.csv"

    load.write_csv(sample_rows(), output_path)

    assert_that(output_path.exists()).is_true()

    with output_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert_that(rows).is_length(1)
    assert_that(rows[0]["input_author_name"]).is_equal_to("Jane Austen")


def test_write_csv_creates_empty_file_when_no_rows(tmp_path):
    output_path = tmp_path / "output" / "authors.csv"

    load.write_csv([], output_path)

    assert_that(output_path.exists()).is_true()
    assert_that(output_path.read_text(encoding="utf-8")).is_equal_to("")


def test_normalize_sqlite_value_converts_empty_string_to_none():
    assert_that(load.normalize_sqlite_value("")).is_none()


def test_normalize_sqlite_value_converts_bool_to_int():
    assert_that(load.normalize_sqlite_value(True)).is_equal_to(1)
    assert_that(load.normalize_sqlite_value(False)).is_equal_to(0)


def test_write_sqlite_db_creates_table_and_inserts_rows(tmp_path):
    output_path = tmp_path / "output" / "authors.db"

    load.write_sqlite_db(sample_rows(), output_path)

    assert_that(output_path.exists()).is_true()

    with closing(sqlite3.connect(output_path))as connection:
        row = connection.execute(
            """
            SELECT input_author_name, openlibrary_key, death_date
            FROM authors_enriched
            """
        ).fetchone()

    assert_that(row[0]).is_equal_to("Jane Austen")
    assert_that(row[1]).is_equal_to("OL1A")
    assert_that(row[2]).is_none()


def test_write_sqlite_db_creates_empty_table_when_no_rows(tmp_path):
    output_path = tmp_path / "output" / "authors.db"

    load.write_sqlite_db([], output_path)

    assert_that(output_path.exists()).is_true()

    with closing(sqlite3.connect(output_path)) as connection:
        row_count = connection.execute(
            "SELECT COUNT(*) FROM authors_enriched"
        ).fetchone()[0]

    assert_that(row_count).is_equal_to(0)
