import requests
from bs4 import BeautifulSoup
import csv
import os
import pdfplumber
from lxml import etree
from io import BytesIO  # Import BytesIO for handling bytes content

# List of URLs
urls = [
    "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000096223/7103b0ff-91b7-4e73-8f38-2a633fee9574.pdf",
    "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000096223/ffa83516-7b50-46f7-b4fe-98132eaf09c7.pdf",
    "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000096223/128143fd-0fd9-4c8f-aab5-fe58845d0b9c.pdf",
    "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000096223/f8f54136-2c65-49ca-bc0a-2c93019cb2d2.pdf"
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
    row_index = 2
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["pdfName", "URL", "Extracted Text"])

# Process each URL
for url in urls:
    # Fetch the webpage content
    response = requests.get(url)
    
    # If the content is HTML
    if 'html' in response.headers['Content-Type']:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from paragraph tags
        text = ' '.join(p.get_text() for p in soup.find_all('p'))
    
    # If the content is PDF
    elif 'pdf' in response.headers['Content-Type']:
        # Use BytesIO to handle the PDF content as a file-like object
        pdf_file = BytesIO(response.content)
        with pdfplumber.open(pdf_file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
    
    # If the content is XML (e.g., XSL)
    elif 'xml' in response.headers['Content-Type']:
        root = etree.fromstring(response.content)
        text = ' '.join([elem.text for elem in root.iter() if elem.text])

    else:
        # If it's some other type of content, fallback to plain text
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
