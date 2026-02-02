import numpy as np
import os
import anthropic
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps
from dotenv import load_dotenv
import pdfplumber
import re
import json

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PDF_PATH = str(PROJECT_ROOT / "finances" / "Scotiabank" / "April 2024 e-statement.pdf")



# General ALL PDF text extraction
def extract_text_from_pdf(pdf_path):
    print(f"Opening PDF: {pdf_path}\n")
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages in PDF: {len(pdf.pages)}\n")
        for i, page in enumerate(pdf.pages):
            print(f"--- Page {i+1} ---")
            text = page.extract_text()
            print(text) 
        print("\n")

# Parser for Transactions Section
def parse_transaction_line(line):
    """Parse transaction line using position-based logic."""
    
    # Match date at the start
    date_match = re.match(r'^([A-Z][a-z]{2})(\d{1,2})\s+', line)
    if not date_match:
        return None
    
    date = f"{date_match.group(1)} {date_match.group(2)}"
    pos = date_match.end()  # Position after date and space
    
    # Extract transaction type (everything until we hit a number)
    type_match = re.match(r'([^\d]+)', line[pos:])
    if not type_match:
        return None
    
    transaction_type = type_match.group(1).strip()
    pos += type_match.end()
    
    # Extract amount (first number with decimals or integer)
    amount_match = re.match(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+', line[pos:])
    if not amount_match:
        return None
    
    amount = amount_match.group(1).replace(',', '')
    pos += amount_match.end()
    
    # Extract balance (second number with decimals or integer)
    balance_match = re.match(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*', line[pos:])
    if not balance_match:
        return None
    
    balance = balance_match.group(1).replace(',', '')
    pos += balance_match.end()
    
    # Everything after is the store/location
    store_location = line[pos:].strip()
    
    # Extract location from store if present
    location = ""
    store = store_location
    
    location_match = re.search(r'([A-Z]{2}(?:CA)?)$', store_location)
    if location_match:
        location = location_match.group(1)
        store = store_location[:location_match.start()].strip()
    
    return {
        "date": date,
        "type": transaction_type,
        "amount": amount,
        "balance": balance,
        "store": store,
        "location": location
    }


# Specific Transactions Section Extraction
def extract_transactions_section(pdf_path):
    print(f"Extracting Transactions Section from PDF: {pdf_path}\n")
    all_transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages in PDF: {len(pdf.pages)}\n")
        for i, page in enumerate(pdf.pages):
            print(f"--- Page {i+1} ---")
            text = page.extract_text()

            start_transactions = "Balance($)"
            end_transactions_1 = "continuedonnextpage"
            end_transactions_2 = "ClosingBalance"
            # Start and end to extract transactions section

            try:
                start_index = text.find(start_transactions)
                end_index_1 = text.find(end_transactions_1)
                end_index_2 = text.find(end_transactions_2)

                if start_index != -1 and end_index_1 != -1:
                    # Extract transactions section
                    transactions_text = text[start_index + len(start_transactions):end_index_1].strip()
                    # transactions_text = transactions_text.replace(' ', '\n')  
                    # print("Extracted Transactions Section:")
                    # print(transactions_text)
                elif start_index != -1 and end_index_2 != -1:
                    # if no end index 1, try end index 2
                    transactions_text = text[start_index + len(start_transactions):end_index_2].strip()
                    # transactions_text = transactions_text.replace(' ', '\n')  
                    # print("Extracted Transactions Section:")
                    # print(transactions_text)
                elif start_index != -1:
                    # if no end index, extract till end of page
                    transactions_text = text[start_index + len(start_transactions):].strip()
                    # transactions_text = transactions_text.replace(' ', '\n')
                    # print("Extracted Transactions Section (till end of page):")
                    # print(transactions_text)
                else:
                    print("Transactions section not found on this page.")
                    continue

                # Convert to a single line for easier viewing
                transactions_text = transactions_text.replace('\n', ' ')

                # Insert new lines before each date pattern
                transactions_text = re.sub(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)+\d{1,2})', r'\n\1', transactions_text)

                # # transactions_text = transactions_text.strip()
                # print("Formatted Transactions Section:")
                # print(transactions_text)

                # Parse each line into JSON
                lines = transactions_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        parsed = parse_transaction_line(line)
                        if parsed:
                            all_transactions.append(parsed)
                            print(json.dumps(parsed, indent=2))
                        else:
                            print(f"Could not parse: {line}")

            except Exception as e:
                print(f"Error extracting transactions: {e}")
            print("\n")


if __name__ == "__main__":
    # extract_text_from_pdf(PDF_PATH)
    extract_transactions_section(PDF_PATH)
