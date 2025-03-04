import requests
from bs4 import BeautifulSoup
import csv
import os

# List of URLs
urls = [
    'https://www.sec.gov/Archives/edgar/data/96223/000114036123040200/brhc20057666_424b2.htm'
    # "https://www.sec.gov/Archives/edgar/data/96223/000114036125006724/ef20044631_fwp.htm",
    # "https://www.sec.gov/Archives/edgar/data/96223/000114036125006462/ef20044714_424b2.htm",
    # "https://www.sec.gov/Archives/edgar/data/96223/000114036125004817/ny20036825x3_ars.pdf",
    # "https://www.sec.gov/Archives/edgar/data/96223/000108514625001584/xslForm13F_X02/primary_doc.xml"
]

# CSV file name
csv_filename = 'pdfGroundTruth.csv'

# Check if the CSV file exists to avoid overwriting
if os.path.exists(csv_filename):
    # Read existing rows to determine the next index
    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
        row_index = len(rows)  # Starting row index is the current row count
else:
    # Create the file and add headers if it doesn't exist
    row_index = 1
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["pdfName", "URL", "Extracted Text"])

# Process each URL
for url in urls:
    # Fetch the webpage content
    response = requests.get(url)
    
    # Handle different content types (HTML or XML)
    if 'html' in response.headers['Content-Type']:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from paragraph tags
        text = ' '.join(p.get_text() for p in soup.find_all('p'))
    else:
        # For non-HTML content, treat as plain text or handle accordingly
        text = response.text

    # Clean the extracted text
    cleaned_text = ' '.join(text.splitlines()).strip()

    # Prepare the name (starts with 'jefferies' followed by the current row number in the CSV)
    name = f"jefferies{row_index}"

    # Append the new data to the CSV
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([name, url, cleaned_text])

    row_index += 1

print(f"Text extracted and saved to {csv_filename}.")
