from src import transform
from assertpy import assert_that


def test_clean_text_removes_multiline_spaces():
    text = "Line one\n\nLine two\t Line three"

    clean = transform.clean_text(text)

    assert_that(clean).is_equal_to("Line one Line two Line three")


def test_get_bio_extracts_dict_value_and_cleans_text():
    bio = transform.get_bio({
        "bio": {
            "value": "Line one\n\nLine two"
        }
    })

    assert_that(bio).is_equal_to("Line one Line two")


def test_build_output_row_returns_not_found_when_no_match():
    row = transform.build_output_row(
        input_author_name="Unknown Author",
        match=None,
    )

    assert_that(row["confidence_level"]).is_equal_to("not_found")
    assert_that(row["enrichment_status"]).is_equal_to("not_found")
    assert_that(row["source"]).is_equal_to("openlibrary")


def test_build_output_row_returns_enriched_row():
    match = {
        "key": "OL1A",
        "author_name": "Jane Austen",
        "match_score": 0.99,
        "score_gap": 0.10,
        "candidate_count": 3,
        "confidence_level": "high_confidence",
    }

    author_details = {
        "birth_date": "1775",
        "death_date": "1817",
        "bio": "English novelist",
    }

    row = transform.build_output_row(
        input_author_name="Jane Austen",
        match=match,
        author_details=author_details,
    )

    assert_that(row["openlibrary_key"]).is_equal_to("OL1A")
    assert_that(row["matched_author_name"]).is_equal_to("Jane Austen")
    assert_that(row["enrichment_status"]).is_equal_to("enriched")
    assert_that(row["bio"]).is_equal_to("English novelist")


class FakeOpenLibrary:
    def __init__(self):
        self.details_called = False

    def search_author_candidates(self, author_name: str) -> list[dict]:
        return [
            {"key": "OL1A", "name": "Jane Austen", "work_count": 1000}
        ]

    def get_author_details(self, author_key: str) -> dict:
        self.details_called = True
        return {
            "birth_date": "1775",
            "death_date": "1817",
            "bio": "English novelist",
        }


def test_enrich_author_fetches_details_for_high_confidence_match():
    openlibrary = FakeOpenLibrary()

    row = transform.enrich_author(
        author_name="Jane Austen",
        openlibrary=openlibrary,
    )

    assert_that(openlibrary.details_called).is_true()
    assert_that(row["confidence_level"]).is_equal_to("high_confidence")
    assert_that(row["enrichment_status"]).is_equal_to("enriched")


class FakeOpenLibraryWithoutCandidates:
    def search_author_candidates(self, author_name: str) -> list[dict]:
        return []

    def get_author_details(self, author_key: str) -> dict:
        raise AssertionError("Details endpoint should not be called")


def test_enrich_author_returns_not_found_when_no_candidates():
    openlibrary = FakeOpenLibraryWithoutCandidates()

    row = transform.enrich_author(
        author_name="Unknown Author",
        openlibrary=openlibrary,
    )

    assert_that(row["confidence_level"]).is_equal_to("not_found")
    assert_that(row["enrichment_status"]).is_equal_to("not_found")
