from difflib import SequenceMatcher
from unicodedata import normalize as unicode_normalize


NAME_WEIGHT = 0.90
WORK_COUNT_WEIGHT = 0.10
WORK_COUNT_K = 100


def normalize_name(name: str) -> str:
    """
    Normalize an author name for comparison.
    :param name: Author name to normalize.
    :return: Normalized author name.
    """
    name = unicode_normalize("NFKD", name or "")
    name = name.encode(encoding="ascii", errors="ignore").decode("ascii")
    name = name.lower().replace(".", " ")
    return " ".join(name.split())


def score_name(input_name: str, candidate_name: str) -> float:
    """
    Calculate the similarity score between two author names.
    :param input_name: Input author name.
    :param candidate_name: Candidate author name.
    :return: Similarity score between 0 and 1.
    """
    input_name = normalize_name(input_name)
    candidate_name = normalize_name(candidate_name)
    score = SequenceMatcher(None, input_name, candidate_name).ratio()
    return round(score, 4)


def score_work_count(work_count: int) -> float:
    """
    Calculate a normalized score based on the author's work count.
    :param work_count: Number of works associated with the candidate author.
    :return: Normalized work count score between 0 and 1.
    """
    work_count = work_count or 0
    return work_count / (work_count + WORK_COUNT_K)


def score_candidate(input_name: str, candidate: dict) -> float:
    """
    Calculate the final score for a candidate author.
    :param input_name: Input author name.
    :param candidate: Candidate author returned by Open Library.
    :return: Weighted candidate score between 0 and 1.
    """
    name_score = score_name(input_name, candidate.get("name", ""))
    work_count_score = score_work_count(candidate.get("work_count", 0))

    final_score = name_score * NAME_WEIGHT + work_count_score * WORK_COUNT_WEIGHT

    return round(final_score, 4)


def get_confidence_level(final_score: float, score_gap: float, candidate_count: int) -> str:
    """
    Determine the confidence level of the selected candidate.
    :param final_score: Final score of the best candidate.
    :param score_gap: Difference between the best and second-best candidate scores.
    :param candidate_count: Number of candidate authors found.
    :return: Confidence level for the selected candidate.
    """
    if candidate_count == 0:
        return "not_found"

    if candidate_count > 1 and score_gap < 0.05:
        return "ambiguous"

    if final_score >= 0.90:
        return "high_confidence"

    if final_score >= 0.80:
        return "medium_confidence"

    return "low_confidence"


def select_best_match(input_name: str, candidates: list[dict]) -> dict:
    """
    Select the best matching author candidate.
    :param input_name: Input author name.
    :param candidates: Candidate authors returned by Open Library.
    :return: Dictionary containing the selected match and its scoring metadata.
    """
    if not candidates:
        return {}
    best_candidate = {}
    best_score = -1.0
    second_best_score = 0.0

    for candidate in candidates:
        score = score_candidate(input_name=input_name, candidate=candidate)

        if best_score < score:
            second_best_score = best_score
            best_score = score
            best_candidate = candidate

        elif second_best_score < score:
            second_best_score = score

    score_gap = round(best_score - second_best_score, 4)

    return {
        "key": best_candidate["key"],
        "author_name": best_candidate["name"],
        "match_score": best_score,
        "second_best_score": second_best_score,
        "score_gap": score_gap,
        "candidate_count": len(candidates),
        "confidence_level": get_confidence_level(
            final_score=best_score,
            score_gap=score_gap,
            candidate_count=len(candidates)
        )
    }
