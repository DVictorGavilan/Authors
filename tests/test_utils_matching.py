from src import utils_matching
from assertpy import assert_that


def test_normalize_name_removes_accents_dots_and_extra_spaces():
    normalized = utils_matching.normalize_name("  J. K.   García Márquez  ")

    assert_that(normalized).is_equal_to("j k garcia marquez")


def test_score_name_returns_one_for_equal_normalized_names():
    score = utils_matching.score_name("J. K. Rowling", "j k rowling")

    assert_that(score).is_equal_to(1.0)


def test_score_work_count_returns_saturated_score():
    score = utils_matching.score_work_count(100)

    assert_that(score).is_equal_to(0.5)


def test_get_confidence_level_returns_ambiguous_when_score_gap_is_low():
    confidence = utils_matching.get_confidence_level(
        final_score=0.95,
        score_gap=0.01,
        candidate_count=2,
    )

    assert_that(confidence).is_equal_to("ambiguous")


def test_get_confidence_level_returns_high_confidence():
    confidence = utils_matching.get_confidence_level(
        final_score=0.95,
        score_gap=0.10,
        candidate_count=2,
    )

    assert_that(confidence).is_equal_to("high_confidence")


def test_select_best_match_returns_empty_dict_when_no_candidates():
    match = utils_matching.select_best_match("Jane Austen", [])

    assert_that(match).is_equal_to({})


def test_select_best_match_returns_best_candidate():
    candidates = [
        {"key": "OL1A", "name": "Jane Austin", "work_count": 20},
        {"key": "OL2A", "name": "Jane Austen", "work_count": 1000},
    ]

    match = utils_matching.select_best_match("Jane Austen", candidates)

    assert_that(match["key"]).is_equal_to("OL2A")
    assert_that(match["author_name"]).is_equal_to("Jane Austen")
    assert_that(match["confidence_level"]).is_equal_to("high_confidence")


def test_get_confidence_level_returns_not_found_when_no_candidates():
    confidence = utils_matching.get_confidence_level(
        final_score=0.0,
        score_gap=0.0,
        candidate_count=0,
    )

    assert_that(confidence).is_equal_to("not_found")


def test_get_confidence_level_returns_medium_confidence():
    confidence = utils_matching.get_confidence_level(
        final_score=0.85,
        score_gap=0.10,
        candidate_count=2,
    )

    assert_that(confidence).is_equal_to("medium_confidence")


def test_get_confidence_level_returns_low_confidence():
    confidence = utils_matching.get_confidence_level(
        final_score=0.70,
        score_gap=0.10,
        candidate_count=2,
    )

    assert_that(confidence).is_equal_to("low_confidence")


def test_select_best_match_tracks_second_best_score():
    candidates = [
        {"key": "OL1A", "name": "Jane Austen", "work_count": 1000},
        {"key": "OL2A", "name": "Jane Austin", "work_count": 20},
    ]

    match = utils_matching.select_best_match("Jane Austen", candidates)

    assert_that(match["key"]).is_equal_to("OL1A")
    assert_that(match["second_best_score"]).is_greater_than(0)
    assert_that(match["match_score"]).is_greater_than(match["second_best_score"])
