#!/usr/bin/env python3
"""URL Text Extraction Tool.

This module provides functionality to extract clean text content from web URLs.
It handles URL validation, content fetching, and text extraction with error handling.
"""

import logging
import sys
from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
import validators
import trafilatura
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class URLExtractionError(Exception):
    """Base exception class for URL extraction errors."""
    pass

class URLValidator:
    """Validates and normalizes URLs."""
    
    @staticmethod
    def validate(url: str) -> str:
        """Validate and normalize a URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            str: Normalized URL if valid
            
        Raises:
            URLExtractionError: If URL is invalid
        """
        # Basic URL validation
        if not validators.url(url):
            raise URLExtractionError(f"Invalid URL format: {url}")
        
        # Parse and normalize URL
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"
        
        return url

class ContentFetcher:
    """Handles fetching content from URLs."""
    
    def __init__(self, timeout: int = 30):
        """Initialize the content fetcher.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
    
    def fetch(self, url: str) -> str:
        """Fetch content from a URL.
        
        Args:
            url: The URL to fetch content from
            
        Returns:
            str: Raw HTML content
            
        Raises:
            URLExtractionError: If content cannot be fetched
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise URLExtractionError(f"Failed to fetch content: {str(e)}")

class TextExtractor:
    """Extracts clean text content from HTML."""
    
    @staticmethod
    def extract(html: str) -> str:
        """Extract clean text from HTML content.
        
        Args:
            html: Raw HTML content
            
        Returns:
            str: Extracted text content
            
        Raises:
            URLExtractionError: If text extraction fails
        """
        try:
            # Try trafilatura first for better content detection
            text = trafilatura.extract(html)
            
            # Fall back to BeautifulSoup if trafilatura fails
            if text is None:
                soup = BeautifulSoup(html, 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator='\n')
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                text = '\n'.join(line for line in lines if line)
            
            return text
        except Exception as e:
            raise URLExtractionError(f"Text extraction failed: {str(e)}")

class URLTextExtractor:
    """Main class for URL text extraction."""
    
    def __init__(self, timeout: int = 30):
        """Initialize the URL text extractor.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.validator = URLValidator()
        self.fetcher = ContentFetcher(timeout=timeout)
        self.extractor = TextExtractor()
    
    def extract_text(self, url: str) -> str:
        """Extract text content from a URL.
        
        Args:
            url: The URL to extract text from
            
        Returns:
            str: Extracted text content
            
        Raises:
            URLExtractionError: If extraction fails
        """
        try:
            # Validate URL
            validated_url = self.validator.validate(url)
            
            # Fetch content
            html_content = self.fetcher.fetch(validated_url)
            
            # Extract text
            text_content = self.extractor.extract(html_content)
            
            return text_content
        
        except URLExtractionError as e:
            logger.error(f"Extraction failed for URL {url}: {str(e)}")
            raise

def main():
    """Command line interface for URL text extraction."""
    if len(sys.argv) != 2:
        print("Usage: python url_extractor.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    extractor = URLTextExtractor()
    
    try:
        text = extractor.extract_text(url)
        print(text)
    except URLExtractionError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()