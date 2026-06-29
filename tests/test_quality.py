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


def test_get_input_quality_summary_counts_empty_and_duplicates():
    authors = [
        "Jane Austen",
        " jane   austen ",
        "",
        "Gabriel García Márquez",
    ]

    summary = quality.get_input_quality_summary(authors)

    assert_that(summary).is_equal_to({
        "input_total_rows": 4,
        "input_empty_author_names": 1,
        "input_duplicate_normalized_authors": 1,
    })


def test_get_output_quality_summary_counts_enrichment_quality():
    rows = [
        {
            "confidence_level": "high_confidence",
            "enrichment_status": "enriched",
            "birth_date": "1775",
            "death_date": "",
            "bio": "Some bio",
        },
        {
            "confidence_level": "invalid_tag",
            "enrichment_status": "enriched",
            "birth_date": "",
            "death_date": "",
            "bio": "",
        },
        {
            "confidence_level": "ambiguous",
            "enrichment_status": "skipped",
            "birth_date": "",
            "death_date": "",
            "bio": "",
        },
    ]

    summary = quality.get_output_quality_summary(rows)

    assert_that(summary).is_equal_to({
        "output_total_rows": 3,
        "output_invalid_confidence_levels": 1,
        "output_enriched_authors": 2,
        "output_birth_date_missing": 1,
        "output_death_date_missing": 2,
        "output_bio_missing": 1,
    })


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


def test_get_output_table_quality_summary_counts_match_categories():
    rows = [
        {"confidence_level": "high_confidence"},
        {"confidence_level": "high_confidence"},
        {"confidence_level": "ambiguous"},
        {"confidence_level": "not_found"},
    ]

    report = quality.get_output_table_quality_summary(rows)

    report_by_category = {
        row["match_category"]: row
        for row in report
    }

    assert_that(report_by_category["high_confidence"]["records"]).is_equal_to(2)
    assert_that(report_by_category["high_confidence"]["percentage"]).is_equal_to("50.0%")

    assert_that(report_by_category["ambiguous"]["records"]).is_equal_to(1)
    assert_that(report_by_category["ambiguous"]["percentage"]).is_equal_to("25.0%")

    assert_that(report_by_category["not_found"]["records"]).is_equal_to(1)
    assert_that(report_by_category["not_found"]["percentage"]).is_equal_to("25.0%")


def test_get_output_table_quality_summary_returns_na_percentages_when_no_rows():
    report = quality.get_output_table_quality_summary([])

    assert_that(report).is_not_empty()

    for row in report:
        assert_that(row["records"]).is_equal_to(0)
        assert_that(row["percentage"]).is_equal_to("N/A")