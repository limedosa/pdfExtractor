"""Unit tests for URL text extraction functionality."""

import unittest
from unittest.mock import Mock, patch
import requests
from url_extractor import (
    URLValidator,
    ContentFetcher,
    TextExtractor,
    URLTextExtractor,
    URLExtractionError
)

class TestURLValidator(unittest.TestCase):
    """Test the URL validator component."""

    def setUp(self):
        """Set up test cases."""
        self.validator = URLValidator()

    def test_valid_url(self):
        """Test validation of a valid URL."""
        url = "https://example.com"
        result = self.validator.validate(url)
        self.assertEqual(result, url)

    def test_url_without_scheme(self):
        """Test validation of URL without scheme."""
        url = "example.com"
        result = self.validator.validate(url)
        self.assertEqual(result, "https://example.com")

    def test_invalid_url(self):
        """Test validation of invalid URL."""
        url = "not-a-url"
        with self.assertRaises(URLExtractionError):
            self.validator.validate(url)

class TestContentFetcher(unittest.TestCase):
    """Test the content fetcher component."""

    def setUp(self):
        """Set up test cases."""
        self.fetcher = ContentFetcher()

    @patch('requests.Session')
    def test_successful_fetch(self, mock_session):
        """Test successful content fetch."""
        mock_response = Mock()
        mock_response.text = "<html>Test content</html>"
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.fetcher.fetch("https://example.com")
        self.assertEqual(result, "<html>Test content</html>")

    @patch('requests.Session')
    def test_failed_fetch(self, mock_session):
        """Test failed content fetch."""
        mock_session.return_value.get.side_effect = \
            requests.exceptions.RequestException("Network error")

        with self.assertRaises(URLExtractionError):
            self.fetcher.fetch("https://example.com")

    @patch('requests.Session')
    def test_http_error(self, mock_session):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = \
            requests.exceptions.HTTPError("404 Not Found")
        mock_session.return_value.get.return_value = mock_response

        with self.assertRaises(URLExtractionError):
            self.fetcher.fetch("https://example.com")

class TestTextExtractor(unittest.TestCase):
    """Test the text extractor component."""

    def setUp(self):
        """Set up test cases."""
        self.extractor = TextExtractor()

    def test_extract_with_trafilatura(self):
        """Test text extraction using trafilatura."""
        html = "<html><body><article>Test content</article></body></html>"
        with patch('trafilatura.extract', return_value="Test content"):
            result = self.extractor.extract(html)
            self.assertEqual(result, "Test content")

    def test_extract_with_beautifulsoup_fallback(self):
        """Test text extraction using BeautifulSoup fallback."""
        html = "<html><body><p>Test content</p></body></html>"
        with patch('trafilatura.extract', return_value=None):
            result = self.extractor.extract(html)
            self.assertEqual(result.strip(), "Test content")

    def test_extract_with_complex_html(self):
        """Test extraction with complex HTML structure."""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <nav>Menu items</nav>
                <main>
                    <article>Main content</article>
                </main>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        with patch('trafilatura.extract', return_value="Main content"):
            result = self.extractor.extract(html)
            self.assertEqual(result, "Main content")

    def test_failed_extraction(self):
        """Test failed text extraction."""
        html = "invalid html"
        with patch('trafilatura.extract', side_effect=Exception("Extraction error")):
            with self.assertRaises(URLExtractionError):
                self.extractor.extract(html)

class TestURLTextExtractor(unittest.TestCase):
    """Test the main URL text extractor."""

    def setUp(self):
        """Set up test cases."""
        self.extractor = URLTextExtractor()

    @patch('url_extractor.ContentFetcher')
    def test_successful_extraction(self, mock_fetcher):
        """Test successful text extraction from URL."""
        mock_fetcher.return_value.fetch.return_value = "<html>Test content</html>"
        
        with patch('url_extractor.TextExtractor.extract', return_value="Test content"):
            result = self.extractor.extract_text("https://example.com")
            self.assertEqual(result, "Test content")

    def test_invalid_url_extraction(self):
        """Test extraction with invalid URL."""
        with self.assertRaises(URLExtractionError):
            self.extractor.extract_text("not-a-url")

    @patch('url_extractor.ContentFetcher')
    def test_network_error_handling(self, mock_fetcher):
        """Test handling of network errors."""
        mock_fetcher.return_value.fetch.side_effect = \
            URLExtractionError("Network error")

        with self.assertRaises(URLExtractionError):
            self.extractor.extract_text("https://example.com")

if __name__ == '__main__':
    unittest.main()