import requests


class OpenLibraryClient:
    BASE_URL = "https://openlibrary.org"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "author-enrichment-pipeline/1.0",
            "Accept": "application/json",
        })

    def search_author_candidates(self, author_name: str) -> list:
        """
        Search for author candidates using the Open Library Authors API.
        :param author_name: Name of the author to search for.
        :return: List of author candidate records returned by Open Library.
        """
        params = {"q": author_name}
        url = f"{self.BASE_URL}/search/authors.json"
        response = self.session.get(url, params=params, timeout=(15, 30))
        response.raise_for_status()
        return response.json().get("docs", [])

    def get_author_details(self, author_key: str) -> dict:
        """
        Retrieve detailed information for an author from the Open Library Authors API.
        :param author_key: Open Library author key (e.g. "OL23919A").
        :return: Dictionary containing the author's details.
        """
        url = f"{self.BASE_URL}/authors/{author_key}.json"
        response = self.session.get(url, timeout=(15, 30))
        response.raise_for_status()
        return response.json()
