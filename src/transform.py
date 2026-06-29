import re
import logging
import hashlib

from src import utils_matching
from src.openlibrary import OpenLibraryClient


def hash_value(value: str | None) -> str:
    """
    Generate a short SHA-256 hash for a string value.
    :param value: Value to hash.
    :return: First 12 characters of the SHA-256 hash.
    """
    value = value or ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def clean_text(value: object) -> str:
    """
    Clean text by normalizing whitespace and trimming leading and trailing spaces.
    :param value: Value to clean.
    :return: Cleaned text value.
    """
    return re.sub(r"\s+", " ", str(value or "")).strip()


def get_bio(author_details: dict) -> str:
    """
    Extract and clean the biography from author details.
    :param author_details: Dictionary containing author details from Open Library.
    :return: Cleaned biography text.
    """
    bio = author_details.get("bio", "")

    if isinstance(bio, dict):
        bio = bio.get("value", "")

    return clean_text(bio)


def build_output_row(input_author_name: str, match: dict | None, author_details: dict | None = None) -> dict:
    """
    Build the output row for an input author.
    :param input_author_name: Original author name from the input file.
    :param match: Selected author match, or None when no match was found.
    :param author_details: Author details returned by Open Library.
    :return: Dictionary representing the enriched output row.
    """
    author_details = author_details or {}

    if not match:
        return {
            "input_author_name": input_author_name,
            "openlibrary_key": "",
            "matched_author_name": "",
            "match_score": "",
            "score_gap": "",
            "candidate_count": 0,
            "confidence_level": "not_found",
            "enrichment_status": "not_found",
            "birth_date": "",
            "death_date": "",
            "bio": "",
            "source": "openlibrary"
        }

    return {
        "input_author_name": input_author_name,
        "openlibrary_key": match.get("key", ""),
        "matched_author_name": match.get("author_name", ""),
        "match_score": match.get("match_score", ""),
        "score_gap": match.get("score_gap", ""),
        "candidate_count": match.get("candidate_count", ""),
        "confidence_level": match.get("confidence_level", ""),
        "enrichment_status": "enriched" if author_details else "skipped",
        "birth_date": author_details.get("birth_date", ""),
        "death_date": author_details.get("death_date", ""),
        "bio": get_bio(author_details),
        "source": "openlibrary"
    }


def enrich_author(author_name: str, openlibrary: OpenLibraryClient) -> dict:
    """
    Enrich an author using Open Library candidate search and detail lookup.
    :param author_name: Author name to enrich.
    :param openlibrary: Open Library client used to search candidates and retrieve author details.
    :return: Dictionary representing the enriched author row.
    """
    author_hash = hash_value(author_name)
    logging.info("Processing author: %s", author_hash)

    candidates = openlibrary.search_author_candidates(author_name)
    match = utils_matching.select_best_match(author_name, candidates)

    if not match:
        logging.warning("No candidates found for author: %s", author_hash)
        return build_output_row(input_author_name=author_name, match=None)

    logging.info(
        "Selected match: input='%s' confidence='%s' score=%s gap=%s candidates=%s",
        author_hash,
        match.get("confidence_level"),
        match.get("match_score"),
        match.get("score_gap", ""),
        match.get("candidate_count")
    )

    author_details = None

    if match.get("confidence_level") == "high_confidence":
        author_details = openlibrary.get_author_details(match["key"])
    else:
        logging.warning(
            "Skipping enrichment for '%s' due to confidence='%s'",
            author_hash,
            match.get("confidence_level")
        )

    return build_output_row(
        input_author_name=author_name,
        match=match,
        author_details=author_details
    )
