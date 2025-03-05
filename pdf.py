import requests
from bs4 import BeautifulSoup
import csv
import os
import pdfplumber
from lxml import etree
from io import BytesIO  # Import BytesIO for handling bytes content

# List of URLs
urls = [
    "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000096223/31fa64d7-9b1c-434d-92c2-d3f4b0bc2837.pdf",
    "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000096223/10b8964c-7d3d-4529-97a3-8f81f9abd12c.pdf",
    "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000096223/5fbc4f92-223a-4259-bd7b-cbf4e8570fdb.pdf",
    "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000096223/99dcdd85-a311-4e02-a541-e3fdaf2cc978.pdf"

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
