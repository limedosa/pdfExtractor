# -*- coding: utf-8 -*-
"""JefferiesDocsPreprocessing.ipynb"""

import os
import json
import csv
import re
import time
import random
import logging
import base64
import requests
import difflib
import botocore.exceptions
import pandas as pd
import cv2
from io import BytesIO
from PIL import Image
from IPython.display import display
from google.colab.patches import cv2_imshow
from google.colab import auth
from google.colab import userdata
from google.auth import default
import boto3
import fitz
import pytesseract
import dotenv
import gspread
import pdfplumber
from datasets import load_dataset, DatasetDict, load_from_disk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
MAX_TOKENS = 10000
MAX_OUTPUT_TOKENS = 2000
MAX_CALLS_PER_MINUTE = 10
MAX_CONTEXT_WORDS = 150000
MAX_OUTPUT_WORDS = 6200
MIN_BACKOFF_TIME = 5
MAX_RETRIES = 15
DELAY_BETWEEN_CALLS = 1
MAX_BATCH_SIZE = 3

# Rate limiting state
last_call_timestamps = []
consecutive_failures = 0

# Setup Google and AWS connections
def setup_connections():
    """Initialize Google Drive and AWS connections"""
    from google.colab import drive
    drive.mount('/content/drive')
    
    auth.authenticate_user()
    creds, _ = default()
    gc = gspread.authorize(creds)
    
    aws_access_key_id = userdata.get('AWS_BEDROCK_KEY')
    aws_secret_access_key = userdata.get('AWS_SECRET_ACCESS_KEY')
    aws_region_name = userdata.get('AWS_REGION')
    
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    bedrock_client = boto3.client(
        service_name="bedrock",
        region_name=aws_region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    return gc, bedrock, bedrock_client

def count_words(text):
    """Count number of words in text."""
    return len(text.split())

def enforce_rate_limit():
    """Enforce rate limiting for API calls with adaptive backoff."""
    global consecutive_failures
    current_time = time.time()
    
    dynamic_delay = DELAY_BETWEEN_CALLS * (2 ** consecutive_failures)
    dynamic_delay = min(dynamic_delay, 30)
    
    if last_call_timestamps:
        time_since_last_call = current_time - last_call_timestamps[-1]
        if time_since_last_call < dynamic_delay:
            sleep_time = dynamic_delay - time_since_last_call
            logger.debug(f"Enforcing dynamic delay: {sleep_time:.2f}s (after {consecutive_failures} failures)")
            time.sleep(sleep_time)
    
    while last_call_timestamps and current_time - last_call_timestamps[0] > 60:
        last_call_timestamps.pop(0)
    
    if len(last_call_timestamps) >= MAX_CALLS_PER_MINUTE:
        sleep_time = 60 - (current_time - last_call_timestamps[0])
        if sleep_time > 0:
            logger.debug(f"Rate limit reached, waiting {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            current_time = time.time()
            while last_call_timestamps and current_time - last_call_timestamps[0] > 60:
                last_call_timestamps.pop(0)

def invoke_model_with_retry(payload, model_id, bedrock, max_retries=MAX_RETRIES):
    """Invoke model with retries, rate limiting, and size checks."""
    global consecutive_failures
    retries = 0
    
    if 'messages' in payload and payload['messages'][0]['content']:
        content = payload['messages'][0]['content']
        total_text = ' '.join(item.get('text', '') for item in content if isinstance(item, dict) and 'text' in item)
        if count_words(total_text) > MAX_CONTEXT_WORDS:
            raise ValueError(f"Input exceeds maximum context size of {MAX_CONTEXT_WORDS:,} words")
    
    while retries < max_retries:
        try:
            enforce_rate_limit()
            last_call_timestamps.append(time.time())
            
            if payload.get('max_tokens', 0) > MAX_TOKENS:
                payload['max_tokens'] = MAX_TOKENS
            
            response = bedrock.invoke_model(
                modelId=model_id,
                contentType="application/json",
                body=json.dumps(payload)
            )
            output_binary = response["body"].read()
            output_json = json.loads(output_binary)
            output_text = output_json["content"][0]["text"]
            
            if count_words(output_text) > MAX_OUTPUT_WORDS:
                raise ValueError(f"Response exceeds maximum size of {MAX_OUTPUT_WORDS:,} words")
            
            consecutive_failures = 0
            return output_text
            
        except bedrock.exceptions.ThrottlingException:
            consecutive_failures += 1
            wait_time = MIN_BACKOFF_TIME * (2 ** consecutive_failures) + random.uniform(0, 1)
            logger.warning(f"ThrottlingException (failure #{consecutive_failures}): Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            retries += 1
        except ValueError as ve:
            raise ve
        except Exception as e:
            consecutive_failures += 1
            logger.error(f"Error during model invocation (failure #{consecutive_failures}): {str(e)}")
            if retries < max_retries - 1:
                wait_time = MIN_BACKOFF_TIME * (2 ** consecutive_failures) + random.uniform(0, 1)
                time.sleep(wait_time)
                retries += 1
            else:
                raise
    
    raise Exception(f"Max retries ({max_retries}) reached after {consecutive_failures} consecutive failures. Try again later.")

def setup_file_handlers(json_filename, csv_filename):
    """Initialize JSON and CSV file handlers."""
    try:
        with open(json_filename, "r", encoding="utf-8") as f:
            pdf_results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pdf_results = []
    
    csv_fields = ["sample_id", "model_output", "ground_truth", "weighted_token_similarity"]
    csv_file = open(csv_filename, "a", newline="", encoding="utf-8")
    csv_writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
    if csv_file.tell() == 0:
        csv_writer.writeheader()
    
    return pdf_results, csv_file, csv_writer

def normalize_text(text):
    """Normalize text by trimming whitespace and cleaning punctuation."""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*([.,!?;:])\s*', r'\1', text)
    return text

def is_number(token):
    """Check if a token is a number."""
    try:
        float(token)
        return True
    except ValueError:
        return False

def weighted_token_similarity(ground_truth, output):
    """Compute weighted similarity where numeric tokens have extra weight."""
    gt_tokens = re.findall(r'\w+', ground_truth)
    out_tokens = re.findall(r'\w+', output)
    
    total_weight = 0
    matched_weight = 0
    
    for token in gt_tokens:
        weight = 2 if is_number(token) else 1
        total_weight += weight
        if token.lower() in (t.lower() for t in out_tokens):
            matched_weight += weight
    
    similarity = (matched_weight / total_weight) * 100 if total_weight > 0 else 0
    return similarity

def process_pdf_with_pdfplumber(pdf_path):
    """Extract text from PDF using pdfplumber."""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text.strip()

def process_pdf_with_docling(pdf_path):
    """Process PDF using Docling with OCR."""
    pipeline_options = PdfPipelineOptions(do_ocr=True)
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )
    result = converter.convert(pdf_path)
    return result.document.export_to_markdown().strip()

def process_batch(pdf_batch, df, persistent_path, pdf_results, csv_writer, process_func):
    """Process a batch of PDFs and save results."""
    for pdf_name in pdf_batch:
        pdf_path = os.path.join(persistent_path, f"{pdf_name}.pdf")
        
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}, skipping...")
            continue
        
        try:
            ground_truth_value = df[df["pdfName"] == pdf_name]["groundTruth"].iloc[0]
            text = process_func(pdf_path)
            
            norm_output = normalize_text(text)
            norm_gt = normalize_text(ground_truth_value)
            weighted_sim = round(weighted_token_similarity(ground_truth_value, norm_output), 2)
            
            result = {
                "sample_id": pdf_name,
                "model_output": text,
                "ground_truth": ground_truth_value,
                "metrics": {"weighted_token_similarity": weighted_sim}
            }
            pdf_results.append(result)
            
            csv_result = {
                "sample_id": pdf_name,
                "model_output": text,
                "ground_truth": ground_truth_value,
                "weighted_token_similarity": weighted_sim
            }
            csv_writer.writerow(csv_result)
            
            print(f"✅ Processed {pdf_name} | Similarity: {weighted_sim:.2f}%")
            
        except Exception as e:
            print(f"❌ Error processing {pdf_name}: {str(e)}")

def main():
    """Main execution function."""
    gc, bedrock, bedrock_client = setup_connections()
    
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    persistent_path = "/content/drive/MyDrive/jefferies/"
    
    # Load spreadsheet data
    jsonUrl = 'https://docs.google.com/spreadsheets/d/1fhJ4sMXhN2u2D9EsmFFmeDNSG3o3nFZ9J-aTl_GB9w0/edit?gid=718505010#gid=718505010'
    regularUrl = 'https://docs.google.com/spreadsheets/d/1I5pCbijNxZqNJ6hqdFpxcdoyXKcZ6Jl2VN9Io2vyr1M/edit?gid=909191242#gid=909191242'
    
    spreadsheet = gc.open_by_url(regularUrl)
    worksheet = spreadsheet.sheet1
    df = pd.DataFrame(worksheet.get_all_records())
    
    # Process PDFs with different methods
    for method in ['pdfplumber', 'docling']:
        json_filename = os.path.join(persistent_path, f"{method}_results.json")
        csv_filename = os.path.join(persistent_path, f"{method}_results.csv")
        
        pdf_results, csv_file, csv_writer = setup_file_handlers(json_filename, csv_filename)
        
        pdfs_to_process = [f"jefferies{i}" for i in range(8, 11)] + [f"jefferies{i}" for i in range(13, 16)]
        process_func = process_pdf_with_pdfplumber if method == 'pdfplumber' else process_pdf_with_docling
        
        total_pdfs = len(pdfs_to_process)
        for i in range(0, total_pdfs, MAX_BATCH_SIZE):
            pdf_batch = pdfs_to_process[i:i + MAX_BATCH_SIZE]
            print(f"Processing batch: {pdf_batch}")
            process_batch(pdf_batch, df, persistent_path, pdf_results, csv_writer, process_func)
            print(f"✅ Batch {i // MAX_BATCH_SIZE + 1} processed. Waiting before next batch...")
            time.sleep(40)
        
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(pdf_results, f, indent=4)
        
        csv_file.close()
        print(f"✅ All PDFs processed and results saved successfully for {method}!")

if __name__ == "__main__":
    main()
