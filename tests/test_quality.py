import pytest

from src import quality
from assertpy import assert_that


def test_validate_input_file_passes_with_valid_csv(tmp_path):
    input_path = tmp_path / "authors_seed.csv"
    input_path.write_text(
        "author_name\nJane Austen\n",
        encoding="utf-8",
    )

    quality.validate_input_file(input_path)


def test_assert_input_file_exists_raises_when_missing(tmp_path):
    input_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        quality.assert_input_file_exists(input_path)


def test_assert_input_file_not_empty_raises_when_empty(tmp_path):
    input_path = tmp_path / "empty.csv"
    input_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        quality.assert_input_file_not_empty(input_path)


def test_assert_input_has_author_name_column_raises_when_missing_column(tmp_path):
    input_path = tmp_path / "authors_seed.csv"
    input_path.write_text(
        "name\nJane Austen\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        quality.assert_input_has_author_name_column(input_path)


def test_validate_output_files_passes_when_outputs_exist(tmp_path):
    output_csv_path = tmp_path / "authors.csv"
    output_db_path = tmp_path / "authors.db"

    output_csv_path.write_text("data", encoding="utf-8")
    output_db_path.write_text("data", encoding="utf-8")

    quality.validate_output_files(output_csv_path, output_db_path)


def test_assert_output_csv_exists_raises_when_missing(tmp_path):
    output_csv_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        quality.assert_output_csv_exists(output_csv_path)


def test_assert_output_db_exists_raises_when_missing(tmp_path):
    output_db_path = tmp_path / "missing.db"

    with pytest.raises(FileNotFoundError):
        quality.assert_output_db_exists(output_db_path)


def test_format_pass_rate_returns_percentage():
    pass_rate = quality.format_pass_rate(passed=3, total=4)

    assert_that(pass_rate).is_equal_to("75.0%")


def test_format_pass_rate_returns_na_when_total_is_zero():
    pass_rate = quality.format_pass_rate(passed=0, total=0)

    assert_that(pass_rate).is_equal_to("N/A")


def test_output_table_rules_includes_categories_with_zero_records():
    rows = [
        {"confidence_level": "high_confidence"},
    ]

    report = quality.output_table_rules(rows)

    report_by_category = {
        row["match_category"]: row
        for row in report
    }

    assert_that(report_by_category["high_confidence"]["records"]).is_equal_to(1)
    assert_that(report_by_category["ambiguous"]["records"]).is_equal_to(0)
    assert_that(report_by_category["not_found"]["records"]).is_equal_to(0)


def test_output_columns_rules_counts_missing_fields_for_enriched_rows_only():
    rows = [
        {
            "enrichment_status": "enriched",
            "birth_date": "1775",
            "death_date": "1817",
            "bio": "Some bio",
        },
        {
            "enrichment_status": "enriched",
            "birth_date": "",
            "death_date": "",
            "bio": "Some bio",
        },
        {
            "enrichment_status": "enriched",
            "birth_date": "1900",
            "death_date": "",
            "bio": "",
        },
        {
            "enrichment_status": "skipped",
            "birth_date": "",
            "death_date": "",
            "bio": "",
        },
    ]

    report = quality.output_columns_rules(rows)

    report_by_column = {
        row["column"]: row
        for row in report
    }

    assert_that(report_by_column["birth_date"]["passed"]).is_equal_to(2)
    assert_that(report_by_column["birth_date"]["failed"]).is_equal_to(1)
    assert_that(report_by_column["birth_date"]["pass_rate"]).is_equal_to("66.7%")

    assert_that(report_by_column["death_date"]["passed"]).is_equal_to(1)
    assert_that(report_by_column["death_date"]["failed"]).is_equal_to(2)
    assert_that(report_by_column["death_date"]["pass_rate"]).is_equal_to("33.3%")

    assert_that(report_by_column["bio"]["passed"]).is_equal_to(2)
    assert_that(report_by_column["bio"]["failed"]).is_equal_to(1)
    assert_that(report_by_column["bio"]["pass_rate"]).is_equal_to("66.7%")
