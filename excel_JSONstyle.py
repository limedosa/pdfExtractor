import xlrd
import csv
import json
import os

# Define paths
folder_path = r"C:\Users\ldomi\OneDrive - WideNet AI\Documents\GitHub\pdfCreator"
csv_file = os.path.join(folder_path, "groundTruthJson50Docs.csv")

# List of files to process
file_names = [f"jefferies{i}.xls" for i in range(1, 51)]

# Unwanted text to remove
UNWANTED_TEXT = "Created by EDGAR Online, Inc."

# Prepare data for CSV storage
data_rows = []

for file_name in file_names:
    xls_file = os.path.join(folder_path, file_name)
    
    if not os.path.exists(xls_file):
        print(f"File not found: {xls_file}, skipping...")
        continue  # Skip missing files

    # Open the workbook
    wb = xlrd.open_workbook(xls_file)
    file_data = {}

    # Loop through sheets and extract data
    for sheet in wb.sheets():
        sheet_data = []
        for row_idx in range(sheet.nrows):
            row_data = sheet.row_values(row_idx)  # Read row data
            row_text = " ".join(map(str, row_data)).strip()  # Convert row to string
            
            # Remove unwanted text
            if UNWANTED_TEXT in row_text:
                row_text = row_text.replace(UNWANTED_TEXT, "").strip()

            if row_text:  # Avoid adding empty rows
                sheet_data.append(row_text)

        # Store extracted data per sheet
        file_data[sheet.name] = sheet_data

    # Convert extracted data to JSON string
    ground_truth_json = json.dumps(file_data, ensure_ascii=False)

    # Remove .xls from filename and store row
    pdf_name = os.path.splitext(file_name)[0]
    data_rows.append([pdf_name, ground_truth_json])

# Write data to CSV
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["pdfName", "groundTruth"])  # Column headers
    writer.writerows(data_rows)  # Write extracted JSON per file

print(f"Data extracted and saved to: {csv_file}")
