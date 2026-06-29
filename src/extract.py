import csv

from pathlib import Path
from src.utils_matching import normalize_name


REQUIRED_COLUMN = "author_name"


def load_author_names(input_path: Path) -> list[str]:
    """
    Load author names from the input CSV file.
    :param input_path: Path to the input CSV file.
    :return: List of author names extracted from the required column.
    """
    with input_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        return [
            row.get(REQUIRED_COLUMN, "")
            for row in reader
        ]


def get_unique_valid_authors(author_names: list[str]) -> list[str]:
    """
    Remove empty and duplicate author names while preserving the original order.
    :param author_names: List of author names.
    :return: List of unique, non-empty author names.
    """
    authors = []
    seen = set()

    for author_name in author_names:
        author_name = (author_name or "").strip()
        normalized_name = normalize_name(author_name)

        if not normalized_name:
            continue

        if normalized_name in seen:
            continue

        seen.add(normalized_name)
        authors.append(author_name)

    return authors
