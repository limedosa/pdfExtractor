import requests
from bs4 import BeautifulSoup

# URL of the document
url = 'https://www.sec.gov/Archives/edgar/data/96223/000114036125006462/ef20044714_424b2.htm'

# Fetch the content of the page
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract all text
text = soup.get_text()

# Print the extracted text
print(text)