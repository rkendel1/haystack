# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock, patch

import pytest
from requests import HTTPError, RequestException, Timeout

from haystack import Document
from haystack.components.websearch.searxng import SearXNGError, SearXNGWebSearch

EXAMPLE_SEARXNG_RESPONSE = {
    "query": "Who is the boyfriend of Olivia Wilde?",
    "number_of_results": 9,
    "results": [
        {
            "url": "https://pagesix.com/2023/01/29/olivia-wilde-hugs-it-out-with-jason-sudeikis-after-harry-styles-split/",
            "title": "Olivia Wilde embraces Jason Sudeikis amid custody battle, Harry Styles split - Page Six",
            "content": "Looks like Olivia Wilde and Jason Sudeikis are starting 2023 on good terms. Amid their highly "
            "publicized custody battle – and the actress' ...",
            "engine": "google",
            "score": 1.0,
        },
        {
            "url": "https://www.yahoo.com/now/olivia-wilde-quietly-dating-again-183844364.html",
            "title": "Olivia Wilde Is 'Quietly Dating' Again Following Harry Styles Split: 'He Makes Her Happy'",
            "content": "Olivia Wilde is \"quietly dating again\" following her November 2022 split from Harry Styles, "
            "a source exclusively tells Life & Style.",
            "engine": "bing",
            "score": 0.95,
        },
        {
            "url": "https://www.usmagazine.com/celebrity-news/pictures/olivia-wilde-and-harry-styles-relationship-timeline/",
            "title": "Olivia Wilde and Harry Styles' Relationship Timeline: The Way They Were - Us Weekly",
            "content": "Olivia Wilde started dating Harry Styles after ending her years-long engagement to Jason "
            "Sudeikis — see their relationship timeline.",
            "engine": "google",
            "score": 0.92,
        },
        {
            "url": "https://www.usmagazine.com/celebrity-news/news/olivia-wilde-is-ready-to-date-again-after-harry-styles-split/",
            "title": "Olivia Wilde Is 'Ready to Date Again' After Harry Styles Split - Us Weekly",
            "content": "Ready for love! Olivia Wilde is officially back on the dating scene following her split from "
            "her ex-boyfriend, Harry Styles.",
            "engine": "duckduckgo",
            "score": 0.9,
        },
        {
            "url": "https://www.harpersbazaar.com/celebrity/latest/a35172115/harry-styles-olivia-wilde-relationship-timeline/",
            "title": "Harry Styles and Olivia Wilde's Definitive Relationship Timeline - Harper's Bazaar",
            "content": "November 2020: News breaks about Olivia splitting from fiancé Jason Sudeikis. ... "
            "In mid-November, news breaks of Olivia Wilde's split from Jason ...",
            "engine": "google",
            "score": 0.88,
        },
        {
            "url": "https://people.com/music/harry-styles-olivia-wilde-relationship-timeline/",
            "title": "Harry Styles and Olivia Wilde's Relationship Timeline - People",
            "content": "Harry Styles and Olivia Wilde first met on the set of Don't Worry Darling and stepped out as "
            "a couple in January 2021. Relive all their biggest relationship ...",
            "engine": "google",
            "score": 0.85,
        },
        {
            "url": "https://people.com/movies/jason-sudeikis-olivia-wilde-relationship-timeline/",
            "title": "Jason Sudeikis and Olivia Wilde's Relationship Timeline - People",
            "content": "Jason Sudeikis and Olivia Wilde ended their engagement of seven years in 2020. Here's a "
            "complete timeline of their relationship.",
            "engine": "bing",
            "score": 0.82,
        },
        {
            "url": "https://www.marca.com/en/lifestyle/celebrities/2023/02/23/63f779a4e2704e8d988b4624.html",
            "title": "Olivia Wilde's anger at ex-boyfriend Harry Styles: She resents him and thinks he was using her "
            "| Marca",
            "content": "The two started dating after Wilde split up with actor Jason Sudeikisin 2020. However, their "
            "relationship came to an end last November.",
            "engine": "google",
            "score": 0.8,
        },
        {
            "url": "https://www.the-sun.com/entertainment/5221040/olivia-wildes-dating-history/",
            "title": "Olivia Wilde's dating history: Who has the actress dated? | The US Sun",
            "content": "AMERICAN actress Olivia Wilde started dating Harry Styles in January 2021 after breaking off "
            "her engagement the year prior.",
            "engine": "google",
            "score": 0.78,
        },
    ],
}


@pytest.fixture
def mock_searxng_search_result():
    with patch("haystack.components.websearch.searxng.requests") as mock_run:
        mock_run.get.return_value = Mock(status_code=200, json=lambda: EXAMPLE_SEARXNG_RESPONSE)
        yield mock_run


@pytest.fixture
def mock_searxng_search_result_no_content():
    resp = {**EXAMPLE_SEARXNG_RESPONSE}
    resp["results"] = [
        {
            "url": "https://example.com",
            "title": "Example Title",
            "engine": "google",
            "score": 1.0,
        }
    ]
    with patch("haystack.components.websearch.searxng.requests") as mock_run:
        mock_run.get.return_value = Mock(status_code=200, json=lambda: resp)
        yield mock_run


class TestSearXNGWebSearch:
    def test_init(self):
        ws = SearXNGWebSearch(base_url="http://localhost:8888")
        assert ws.base_url == "http://localhost:8888"
        assert ws.top_k == 10
        assert ws.allowed_domains is None
        assert ws.exclude_subdomains is False
        assert ws.search_params == {}

    def test_to_dict(self):
        component = SearXNGWebSearch(
            base_url="http://localhost:8888",
            top_k=10,
            allowed_domains=["test.com"],
            search_params={"language": "en"},
        )
        data = component.to_dict()
        assert data == {
            "type": "haystack.components.websearch.searxng.SearXNGWebSearch",
            "init_parameters": {
                "base_url": "http://localhost:8888",
                "top_k": 10,
                "allowed_domains": ["test.com"],
                "exclude_subdomains": False,
                "search_params": {"language": "en"},
            },
        }

    def test_from_dict(self):
        data = {
            "type": "haystack.components.websearch.searxng.SearXNGWebSearch",
            "init_parameters": {
                "base_url": "http://localhost:8888",
                "top_k": 5,
                "allowed_domains": ["example.com"],
                "exclude_subdomains": True,
                "search_params": {"language": "en"},
            },
        }
        component = SearXNGWebSearch.from_dict(data)
        assert component.base_url == "http://localhost:8888"
        assert component.top_k == 5
        assert component.allowed_domains == ["example.com"]
        assert component.exclude_subdomains is True
        assert component.search_params == {"language": "en"}

    @pytest.mark.parametrize("top_k", [1, 5, 7])
    def test_web_search_top_k(self, mock_searxng_search_result, top_k: int):
        ws = SearXNGWebSearch(base_url="http://localhost:8888", top_k=top_k)
        results = ws.run(query="Who is the boyfriend of Olivia Wilde?")
        documents = results["documents"]
        links = results["links"]
        assert len(documents) == len(links) == top_k
        assert all(isinstance(doc, Document) for doc in documents)
        assert all(isinstance(link, str) for link in links)
        assert all(link.startswith("http") for link in links)

    def test_no_content(self, mock_searxng_search_result_no_content):
        ws = SearXNGWebSearch(base_url="http://localhost:8888", top_k=1)
        results = ws.run(query="Who is the boyfriend of Olivia Wilde?")
        documents = results["documents"]
        assert len(documents) == 1
        assert documents[0].content == "Example Title"

    @patch("requests.get")
    def test_timeout_error(self, mock_get):
        mock_get.side_effect = Timeout
        ws = SearXNGWebSearch(base_url="http://localhost:8888")

        with pytest.raises(TimeoutError):
            ws.run(query="Who is the boyfriend of Olivia Wilde?")

    @patch("requests.get")
    def test_request_exception(self, mock_get):
        mock_get.side_effect = RequestException
        ws = SearXNGWebSearch(base_url="http://localhost:8888")

        with pytest.raises(SearXNGError):
            ws.run(query="Who is the boyfriend of Olivia Wilde?")

    @patch("requests.get")
    def test_bad_response_code(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError
        ws = SearXNGWebSearch(base_url="http://localhost:8888")

        with pytest.raises(SearXNGError):
            ws.run(query="Who is the boyfriend of Olivia Wilde?")

    def test_exclude_subdomains_filtering(self):
        """Test that exclude_subdomains parameter properly filters results."""
        # Mock response with mixed domains and subdomains
        mock_response = {
            "query": "test query",
            "number_of_results": 4,
            "results": [
                {
                    "title": "Main domain result",
                    "url": "https://example.com/page1",
                    "content": "Content from main domain",
                    "engine": "google",
                    "score": 1.0,
                },
                {
                    "title": "Subdomain result 1",
                    "url": "https://blog.example.com/post1",
                    "content": "Content from blog subdomain",
                    "engine": "bing",
                    "score": 0.9,
                },
                {
                    "title": "Subdomain result 2",
                    "url": "https://shop.example.com/product1",
                    "content": "Content from shop subdomain",
                    "engine": "duckduckgo",
                    "score": 0.8,
                },
                {
                    "title": "Different domain result",
                    "url": "https://other.com/page1",
                    "content": "Content from different domain",
                    "engine": "google",
                    "score": 0.7,
                },
            ],
        }

        with patch("haystack.components.websearch.searxng.requests") as mock_requests:
            mock_requests.get.return_value = Mock(status_code=200, json=lambda: mock_response)

            # Test with exclude_subdomains=False (default behavior)
            ws_include = SearXNGWebSearch(
                base_url="http://localhost:8888", allowed_domains=["example.com"], exclude_subdomains=False
            )
            results_include = ws_include.run(query="test query")

            # Should include main domain and subdomains but exclude other domains
            assert len(results_include["documents"]) == 3  # example.com + 2 subdomains
            assert len(results_include["links"]) == 3

            included_links = results_include["links"]
            assert "https://example.com/page1" in included_links
            assert "https://blog.example.com/post1" in included_links
            assert "https://shop.example.com/product1" in included_links
            assert "https://other.com/page1" not in included_links

            # Test with exclude_subdomains=True
            ws_exclude = SearXNGWebSearch(
                base_url="http://localhost:8888", allowed_domains=["example.com"], exclude_subdomains=True
            )
            results_exclude = ws_exclude.run(query="test query")

            # Should only include main domain, exclude subdomains and other domains
            assert len(results_exclude["documents"]) == 1  # only example.com
            assert len(results_exclude["links"]) == 1

            excluded_links = results_exclude["links"]
            assert "https://example.com/page1" in excluded_links
            assert "https://blog.example.com/post1" not in excluded_links
            assert "https://shop.example.com/product1" not in excluded_links
            assert "https://other.com/page1" not in excluded_links

    def test_is_domain_allowed_helper_method(self):
        """Test the _is_domain_allowed helper method directly."""
        # Test with exclude_subdomains=False
        ws_include = SearXNGWebSearch(
            base_url="http://localhost:8888",
            allowed_domains=["example.com", "test.org"],
            exclude_subdomains=False,
        )

        # Should allow main domains and subdomains
        assert ws_include._is_domain_allowed("https://example.com/page")
        assert ws_include._is_domain_allowed("https://blog.example.com/post")
        assert ws_include._is_domain_allowed("https://shop.example.com/product")
        assert ws_include._is_domain_allowed("https://test.org/page")
        assert ws_include._is_domain_allowed("https://sub.test.org/page")
        assert not ws_include._is_domain_allowed("https://other.com/page")

        # Test with exclude_subdomains=True
        ws_exclude = SearXNGWebSearch(
            base_url="http://localhost:8888",
            allowed_domains=["example.com", "test.org"],
            exclude_subdomains=True,
        )

        # Should only allow exact domain matches
        assert ws_exclude._is_domain_allowed("https://example.com/page")
        assert not ws_exclude._is_domain_allowed("https://blog.example.com/post")
        assert not ws_exclude._is_domain_allowed("https://shop.example.com/product")
        assert ws_exclude._is_domain_allowed("https://test.org/page")
        assert not ws_exclude._is_domain_allowed("https://sub.test.org/page")
        assert not ws_exclude._is_domain_allowed("https://other.com/page")

        # Test with no allowed_domains (should allow all)
        ws_no_filter = SearXNGWebSearch(base_url="http://localhost:8888", allowed_domains=None)
        assert ws_no_filter._is_domain_allowed("https://any.domain.com/page")
