from src import extract
from assertpy import assert_that


def test_load_author_names_reads_raw_values(tmp_path):
    input_path = tmp_path / "authors_seed.csv"
    input_path.write_text(
        "author_name\n"
        "Jane Austen\n"
        "\"\"\n"
        "   \n"
        "J. K. Rowling\n",
        encoding="utf-8",
    )

    authors = extract.load_author_names(input_path)

    assert_that(authors).is_equal_to([
        "Jane Austen",
        "",
        "   ",
        "J. K. Rowling",
    ])


def test_get_unique_valid_authors_removes_empty_and_duplicates():
    authors = [
        "Jane Austen",
        " jane   austen ",
        "",
        "J. K. Rowling",
        "j k rowling",
        "Gabriel García Márquez",
    ]

    unique_authors = extract.get_unique_valid_authors(authors)

    assert_that(unique_authors).is_equal_to([
        "Jane Austen",
        "J. K. Rowling",
        "Gabriel García Márquez",
    ])
