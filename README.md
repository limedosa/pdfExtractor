# URL Text Extractor

A Python tool for extracting clean text content from web URLs. This tool handles URL validation, content fetching, and text extraction with robust error handling.

## Features

- URL validation and normalization
- Robust content fetching with timeout handling
- Smart text extraction using trafilatura with BeautifulSoup fallback
- Clean content output with preserved formatting
- Comprehensive error handling
- Command-line interface

## Repository Structure

- `url_extractor.py`: Main module containing the URL text extraction functionality
  - `URLValidator`: Handles URL validation and normalization
  - `ContentFetcher`: Manages HTTP requests and content retrieval
  - `TextExtractor`: Processes HTML and extracts clean text
  - `URLTextExtractor`: Main class that orchestrates the extraction process
- `requirements.txt`: Lists project dependencies
- `.gitignore`: Specifies which files Git should ignore
- `.gitattributes`: Defines Git attributes for proper line ending handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/url-text-extractor.git
cd url-text-extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
python url_extractor.py <url>
```

Example:
```bash
python url_extractor.py https://example.com
```

### As a Python Module

```python
from url_extractor import URLTextExtractor

extractor = URLTextExtractor()
try:
    text = extractor.extract_text("https://example.com")
    print(text)
except URLExtractionError as e:
    print(f"Error: {str(e)}")
```

## Requirements

- Python 3.6+
- Dependencies:
  - requests: HTTP library for making requests
  - beautifulsoup4: HTML parsing and navigation
  - trafilatura: Main text extraction engine
  - validators: URL validation utilities
  - urllib3: HTTP client (required by requests)

## Error Handling

The tool handles various error cases:
- Invalid URL formats
- Network connection issues
- Timeout errors
- Content extraction failures

## License

MIT License - feel free to use and modify as needed.