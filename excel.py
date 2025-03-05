import xlrd
import csv
import os

# Define paths
folder_path = r"C:\Users\ldomi\OneDrive - WideNet AI\Documents\GitHub\pdfCreator"
csv_file = os.path.join(folder_path, "groundTruth.csv")

# List of files to process
file_names = [f"jefferies{i}.xls" for i in range(1, 16)]

# Unwanted text to remove
UNWANTED_TEXT = "Created by EDGAR Online, Inc."

# Prepare data for CSV
data_rows = []

for file_name in file_names:
    xls_file = os.path.join(folder_path, file_name)
    
    if not os.path.exists(xls_file):
        print(f"File not found: {xls_file}, skipping...")
        continue  # Skip missing files

    # Open the workbook
    wb = xlrd.open_workbook(xls_file)
    
    # Extract all data into one large string
    all_data = []
    for sheet in wb.sheets():
        for row_idx in range(sheet.nrows):
            row_data = sheet.row_values(row_idx)  # Read row data
            row_text = " ".join(map(str, row_data))  # Convert row to string
            
            # Remove unwanted text
            row_text = row_text.replace(UNWANTED_TEXT, "").strip()

            all_data.append(row_text)

    # Combine all extracted data into one large string
    ground_truth = " ".join(all_data)

    # Remove .xls from filename
    pdf_name = os.path.splitext(file_name)[0]

    # Add to data list
    data_rows.append([pdf_name, ground_truth])

# Write data to CSV
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["pdf name", "groundTruth"])  # Column headers
    writer.writerows(data_rows)  # Write all extracted data

print(f"Data extracted and saved to: {csv_file}")
