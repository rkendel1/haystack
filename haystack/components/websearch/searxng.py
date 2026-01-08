# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional, Union
from urllib.parse import urlparse

import requests

from haystack import ComponentError, Document, component, default_from_dict, default_to_dict, logging

logger = logging.getLogger(__name__)


class SearXNGError(ComponentError): ...


@component
class SearXNGWebSearch:
    """
    Uses [SearXNG](https://docs.searxng.org/) to search the web for relevant documents.

    SearXNG is a free internet metasearch engine which aggregates results from various search services
    and databases. It can be self-hosted for privacy and no API key is required.

    Usage example:
    ```python
    from haystack.components.websearch import SearXNGWebSearch

    # Using a self-hosted SearXNG instance
    websearch = SearXNGWebSearch(base_url="http://localhost:8888")
    results = websearch.run(query="Who is the boyfriend of Olivia Wilde?")

    assert results["documents"]
    assert results["links"]

    # Example with domain filtering - exclude subdomains
    websearch_filtered = SearXNGWebSearch(
        base_url="http://localhost:8888",
        top_k=10,
        allowed_domains=["example.com"],
        exclude_subdomains=True,  # Only results from example.com, not blog.example.com
    )
    results_filtered = websearch_filtered.run(query="search query")
    ```
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8888",
        top_k: Optional[int] = 10,
        allowed_domains: Optional[list[str]] = None,
        search_params: Optional[dict[str, Any]] = None,
        *,
        exclude_subdomains: bool = False,
    ):
        """
        Initialize the SearXNGWebSearch component.

        :param base_url: Base URL of the SearXNG instance (e.g., "http://localhost:8888").
        :param top_k: Number of documents to return.
        :param allowed_domains: List of domains to limit the search to.
        :param exclude_subdomains: Whether to exclude subdomains when filtering by allowed_domains.
            If True, only results from the exact domains in allowed_domains will be returned.
            If False, results from subdomains will also be included. Defaults to False.
        :param search_params: Additional parameters passed to the SearXNG API.
            For example, you can set 'language' to 'en' to limit results to English.
            See the [SearXNG docs](https://docs.searxng.org/) for more details.
        """
        self.base_url = base_url.rstrip("/")
        self.top_k = top_k
        self.allowed_domains = allowed_domains
        self.exclude_subdomains = exclude_subdomains
        self.search_params = search_params or {}

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
                Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            base_url=self.base_url,
            top_k=self.top_k,
            allowed_domains=self.allowed_domains,
            exclude_subdomains=self.exclude_subdomains,
            search_params=self.search_params,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearXNGWebSearch":
        """
        Deserializes the component from a dictionary.

        :returns:
                The deserialized component.
        """
        return default_from_dict(cls, data)

    def _is_domain_allowed(self, url: str) -> bool:
        """
        Check if a URL's domain is allowed based on allowed_domains and exclude_subdomains settings.

        :param url: The URL to check.
        :returns: True if the domain is allowed, False otherwise.
        """
        if not self.allowed_domains:
            return True

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            for allowed_domain in self.allowed_domains:
                allowed_domain = allowed_domain.lower()

                if self.exclude_subdomains:
                    # Exact domain match only
                    if domain == allowed_domain:
                        return True
                else:
                    # Allow subdomains (current behavior)
                    if domain == allowed_domain or domain.endswith("." + allowed_domain):
                        return True

            return False
        except Exception:
            # If URL parsing fails, allow the result to be safe
            return True

    @component.output_types(documents=list[Document], links=list[str])
    def run(self, query: str) -> dict[str, Union[list[Document], list[str]]]:
        """
        Use SearXNG to search the web.

        :param query: Search query.
        :returns: A dictionary with the following keys:
            - "documents": List of documents returned by the search engine.
            - "links": List of links returned by the search engine.
        :raises SearXNGError: If an error occurs while querying the SearXNG API.
        :raises TimeoutError: If the request to the SearXNG API times out.
        """
        # SearXNG API expects parameters as query string
        params = {
            "q": query,
            "format": "json",
            **self.search_params
        }

        try:
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()
        except requests.Timeout as error:
            raise TimeoutError(f"Request to {self.__class__.__name__} timed out.") from error
        except requests.RequestException as e:
            raise SearXNGError(f"An error occurred while querying {self.__class__.__name__}. Error: {e}") from e

        # Parse the response
        json_result = response.json()

        # SearXNG returns results in a 'results' array
        results = json_result.get("results", [])

        # Filter results by domain if needed and convert to Documents
        documents = []
        links = []
        
        for result in results:
            url = result.get("url", "")
            if not self._is_domain_allowed(url):
                continue
            
            # Create document from result
            doc = Document(
                content=result.get("content", result.get("title", "")),
                meta={
                    "title": result.get("title", ""),
                    "url": url,
                    "engine": result.get("engine", ""),
                    "score": result.get("score", 0),
                }
            )
            documents.append(doc)
            links.append(url)

        logger.debug(
            "SearXNG returned {number_documents} documents for the query '{query}'",
            number_documents=len(documents),
            query=query,
        )
        
        return {"documents": documents[: self.top_k], "links": links[: self.top_k]}
