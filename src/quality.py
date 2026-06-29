import csv

from pathlib import Path
from collections import Counter
from src.utils_matching import normalize_name


VALID_CONFIDENCE_LEVELS = [
    "high_confidence",
    "medium_confidence",
    "low_confidence",
    "ambiguous",
    "not_found"
]


def assert_input_file_exists(input_path: str | Path) -> None:
    """
    Validate that the input file exists.
    :param input_path: Path to the input file.
    """
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")


def assert_input_file_not_empty(input_path: str | Path) -> None:
    """
    Validate that the input file is not empty.
    :param input_path: Path to the input file.
    """
    path = Path(input_path)

    if path.stat().st_size == 0:
        raise ValueError(f"Input file is empty: {input_path}")


def assert_input_has_author_name_column(input_path: str | Path) -> None:
    """
    Validate that the input CSV file contains the required author name column.
    :param input_path: Path to the input CSV file.
    """
    path = Path(input_path)

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if "author_name" not in (reader.fieldnames or []):
            raise ValueError("Input file must contain an 'author_name' column.")


def validate_input_file(input_path: str | Path) -> None:
    """
    Validate that the input file exists, is not empty, and contains the required column.
    :param input_path: Path to the input file.
    """
    assert_input_file_exists(input_path)
    assert_input_file_not_empty(input_path)
    assert_input_has_author_name_column(input_path)


def assert_output_csv_exists(output_csv_path: str | Path) -> None:
    """
    Validate that the output CSV file exists.
    :param output_csv_path: Path to the output CSV file.
    """
    if not Path(output_csv_path).exists():
        raise FileNotFoundError(f"Output CSV does not exist: {output_csv_path}")


def assert_output_db_exists(output_db_path: str | Path) -> None:
    """
    Validate that the output SQLite database file exists.
    :param output_db_path: Path to the output SQLite database file.
    """
    if not Path(output_db_path).exists():
        raise FileNotFoundError(f"Output DB does not exist: {output_db_path}")


def validate_output_files(output_csv_path: str | Path, output_db_path: str | Path) -> None:
    """
    Validate that the expected output CSV and SQLite database files exist.
    :param output_csv_path: Path to the output CSV file.
    :param output_db_path: Path to the output SQLite database file.
    """
    assert_output_csv_exists(output_csv_path)
    assert_output_db_exists(output_db_path)


def count_empty_author_names(author_names: list[str]) -> int:
    """
    Count author names that are empty after normalization.
    :param author_names: List of author names to evaluate.
    :return: Number of empty normalized author names.
    """
    return sum(
        1
        for author_name in author_names
        if not normalize_name(author_name)
    )


def count_duplicated_normalized_authors(author_names: list[str]) -> int:
    """
    Count duplicated author names after normalization.
    :param author_names: List of author names to evaluate.
    :return: Number of duplicated normalized author names.
    """
    normalized_names = [
        normalize_name(author_name)
        for author_name in author_names
        if normalize_name(author_name)
    ]

    return len(normalized_names) - len(set(normalized_names))


def count_invalid_confidence_levels(rows: list[dict]) -> int:
    """
    Count rows with invalid confidence levels.
    :param rows: List of enriched author rows.
    :return: Number of rows with invalid confidence levels.
    """
    return sum(
        1
        for row in rows
        if row.get("confidence_level") not in VALID_CONFIDENCE_LEVELS
    )


def count_enriched_authors(rows: list[dict]) -> int:
    """
    Count rows successfully enriched.
    :param rows: List of enriched author rows.
    :return: Number of rows with enriched status.
    """
    return sum(
        1
        for row in rows
        if row.get("enrichment_status") == "enriched"
    )


def count_missing_birth_date(rows: list[dict]) -> int:
    """
    Count enriched rows without a birthdate.
    :param rows: List of enriched author rows.
    :return: Number of enriched rows missing a birthdate.
    """
    return sum(
        1
        for row in rows
        if row.get("enrichment_status") == "enriched"
        and not row.get("birth_date")
    )


def count_missing_death_date(rows: list[dict]) -> int:
    """
    Count enriched rows without a death date.
    :param rows: List of enriched author rows.
    :return: Number of enriched rows missing a death date.
    """
    return sum(
        1
        for row in rows
        if row.get("enrichment_status") == "enriched"
        and not row.get("death_date")
    )


def count_missing_bio(rows: list[dict]) -> int:
    """
    Count enriched rows without a biography.
    :param rows: List of enriched author rows.
    :return: Number of enriched rows missing a biography.
    """
    return sum(
        1
        for row in rows
        if row.get("enrichment_status") == "enriched"
        and not row.get("bio")
    )


def format_pass_rate(passed: int, total: int) -> str:
    """
    Format a pass rate as a percentage string.
    :param passed: Number of records that passed the quality rule.
    :param total: Total number of records evaluated.
    :return: Formatted pass rate percentage, or "N/A" when total is zero.
    """
    if total == 0:
        return "N/A"

    return f"{(passed / total) * 100:.1f}%"


def input_table_rules(raw_authors: list[str], processed_authors: list[str]) -> list[dict]:
    """
    Build a table-friendly quality summary for the input data.
    :param raw_authors: List of raw author names from the input file.
    :param processed_authors: List of unique valid authors processed.
    :return: List of dictionaries representing input quality metrics.
    """
    return [
        {
            "Metric": "Input rows",
            "Value": len(raw_authors),
        },
        {
            "Metric": "Empty author names",
            "Value":  count_empty_author_names(raw_authors),
        },
        {
            "Metric": "Duplicated normalized authors",
            "Value": count_duplicated_normalized_authors(raw_authors),
        },
        {
            "Metric": "Unique valid authors processed",
            "Value": len(processed_authors),
        }
    ]


def output_table_rules(rows: list[dict]) -> list[dict]:
    """
    Build a table-friendly summary of output rows by confidence level.
    :param rows: List of enriched author rows.
    :return: List of dictionaries containing record counts and percentages by confidence level.
    """
    total_rows = len(rows)
    confidence_counts = Counter(
        row.get("confidence_level", "")
        for row in rows
    )

    return [
        {
            "match_category": confidence_level,
            "records": confidence_counts.get(confidence_level, 0),
            "percentage": format_pass_rate(
                confidence_counts.get(confidence_level, 0),
                total_rows,
            ),
        }
        for confidence_level in VALID_CONFIDENCE_LEVELS
    ]


def output_columns_rules(rows: list[dict]) -> list[dict]:
    """
    Build a table-friendly quality summary for selected output columns.
    :param rows: List of enriched author rows.
    :return: List of dictionaries containing column-level quality checks.
    """
    enriched_authors = count_enriched_authors(rows)
    missing_birth_date = count_missing_birth_date(rows)
    missing_death_date = count_missing_death_date(rows)
    missing_bio = count_missing_bio(rows)

    return [
        {
            "column": "birth_date",
            "quality_rule": "Not missing",
            "applies_to": "Output file",
            "passed": enriched_authors - missing_birth_date,
            "failed": missing_birth_date,
            "pass_rate": format_pass_rate(enriched_authors - missing_birth_date, enriched_authors),
            "severity": "No Critical"
        },
        {
            "column": "death_date",
            "quality_rule": "Not missing",
            "applies_to": "Output file",
            "passed": enriched_authors - missing_death_date,
            "failed": missing_death_date,
            "pass_rate": format_pass_rate(enriched_authors - missing_death_date, enriched_authors),
            "severity": "No Critical"
        },
        {
            "column": "bio",
            "quality_rule": "Not missing",
            "applies_to": "Output file",
            "passed": enriched_authors - missing_bio,
            "failed": missing_bio,
            "pass_rate": format_pass_rate(enriched_authors - missing_bio, enriched_authors),
            "severity": "No Critical"
        }
    ]
