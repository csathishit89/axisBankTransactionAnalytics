import psycopg2
import json
import re
import csv
import io
import os
import boto3
import fitz  # PyMuPDF

s3 = boto3.client("s3")

OUTPUT_BUCKET = "axis-bank-pdf-bucket"

# -------------------------------------------------
# Transaction Categories
# -------------------------------------------------
TRANSACTION_CATEGORIES = {
    # Food & Dining
    'FOOD_DELIVERY': ['ZOMATO', 'SWIGGY', 'EATSURE', 'UBER EATS'],
    'RESTAURANTS': ['ANNAPOORNA', 'JUNIOR KUPPANNA', 'SREE ANNAPOORNA', 'HOTEL ANNAPOORNA',
                    'SHREE ANANDHAAS', 'KOVAI BIRIYANI', 'A2B ADYAR ANANDA BHAVAN'],
    'GROCERIES': ['DMART', 'MORE SUPERMARKET', 'SPAR HYPERMARKET', 'RELIANCE FRESH',
                  'NILGIRIS', 'PAZHAMUDIR NILAYAM', 'KOVAI PAZHAMUDIR'],

    # Shopping
    'ONLINE_SHOPPING': ['AMAZON', 'FLIPKART', 'MYNTRA', 'AJIO', 'MEESHO'],

    # Transportation
    'RIDE_HAILING': ['UBER', 'OLA', 'RAPIDO'],
    'FUEL': ['INDIAN OIL', 'BHARAT PETROLEUM', 'HP PETROL', 'SHELL'],

    # Bills & Utilities
    'ELECTRICITY': ['TANGEDCO'],
    'INTERNET': ['ACT FIBERNET', 'ACTBB'],
    'MOBILE_RECHARGE': ['AIRTEL RECHARGE', 'JIO RECHARGE', 'VI RECHARGE'],
    'GAS': ['INDANE GAS'],

    # Healthcare
    'PHARMACY': ['MEDPLUS', 'NETMEDS', 'APOLLO PHARMACY'],
    'HEALTH_INSURANCE': ['HEALTH INSURANCE', 'PREMIUM'],

    # Entertainment & Subscriptions
    'STREAMING': ['NETFLIX', 'HOTSTAR', 'AMAZON PRIME'],
    'ENTERTAINMENT': ['BOOKMYSHOW'],

    # Financial
    'INVESTMENTS': ['AXISMUTUALFUND', 'SIP', 'MUTUAL FUND'],
    'CREDIT_CARD_PAYMENT': ['AXIS CREDIT CARD', 'CREDIT CARD', 'PAYMENT'],
    'SALARY': ['SALARY', 'PSG INDUSTRIES'],
    'BONUS': ['BONUS'],
    'INTEREST': ['INT/CREDIT', 'INTEREST'],

    # Transfers
    'FAMILY_SUPPORT': ['FAMILY SUPPORT'],
    'RECEIVED_MONEY': ['RECEIVED FROM', 'UPI/.*?/RECEIVED'],

    # Banking
    'ATM_WITHDRAWAL': ['ATM/CASH WDL', 'ATM WITHDRAWAL'],
    'BANK_CHARGES': ['CHG/', 'CHARGES', 'SMS ALERT'],
}

def categorize_transaction(description):
    """
    Categorize a transaction based on its description
    Returns the category name or 'OTHER' if no match found
    """
    description_upper = description.upper()

    # Check each category
    for category, keywords in TRANSACTION_CATEGORIES.items():
        for keyword in keywords:
            # Check if keyword is a regex pattern
            if keyword.startswith('UPI/') or '.*?' in keyword:
                if re.search(keyword, description_upper):
                    return category
            else:
                if keyword in description_upper:
                    return category

    # Special handling for specific patterns
    if re.search(r'POS/\d+/', description_upper):
        # POS transactions - try to extract merchant name
        if any(shop in description_upper for shop in ['MYNTRA', 'FLIPKART', 'AMAZON', 'AJIO', 'MEESHO']):
            return 'ONLINE_SHOPPING'
        elif any(food in description_upper for food in ['ANNAPOORNA', 'KUPPANNA', 'ANANDHAAS']):
            return 'RESTAURANTS'
        elif 'FUEL' in description_upper or 'PETROL' in description_upper:
            return 'FUEL'

    if re.search(r'NEFT.*?SALARY', description_upper):
        return 'SALARY'

    if re.search(r'NEFT.*?FAMILY', description_upper):
        return 'FAMILY_SUPPORT'

    return 'OTHER'

def get_category_display_name(category):
    """Convert category code to readable display name"""
    return category.replace('_', ' ').title()

# -------------------------------------------------
# Utility: Safe Regex Search
# -------------------------------------------------
def safe_search(pattern, text, flags=0):
    """Search for a pattern and return the first capture group or empty string"""
    match = re.search(pattern, text, flags)
    return match.group(1).strip() if match else ""

def safe_search_number(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).replace(",", "") if match else None


# -------------------------------------------------
# Extract Text from PDF
# -------------------------------------------------
def extract_text_from_pdf(bucket, key):
    """Extract all text from a PDF file stored in S3"""
    obj = s3.get_object(Bucket=bucket, Key=key)
    pdf = fitz.open(stream=obj["Body"].read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in pdf)
    pdf.close()
    return text

# -------------------------------------------------
# Parse Account Info
# -------------------------------------------------
def parse_account_info(text):
    """Extract account information from the statement"""
    return {
        "account_holder": safe_search(r"Account Holder:\s*(.+?)(?:\s+Account Number|$)", text),
        "account_number": safe_search(r"Account Number:\s*(\d+)", text),
        "account_type": safe_search(r"Account Type:\s*(.+?)(?:\s+IFSC|$)", text),
        "ifsc": safe_search(r"IFSC Code:\s*(\w+)", text),
        "branch": safe_search(r"Branch:\s*(.+?)(?:\s+Statement|$)", text),
        "statement_period": safe_search(r"Statement Period:\s*(.+?)(?:\s+Customer|$)", text),
        "customer_id": safe_search(r"Customer ID:\s*(\w+)", text),
        "currency": safe_search(r"Currency:\s*(\w+)", text)
    }

# -------------------------------------------------
# Parse Account Summary
# -------------------------------------------------
def parse_account_summary(text):
    """Extract account summary information"""
    # Updated regex to handle the ■ symbol (black square) used in the PDF
    # return {
    #     "opening_balance": safe_search(r"Opening Balance\s+[■]?([\d,]+\.\d+)", text),
    #     "total_credits": safe_search(r"Total Credits\s+\(\+\)\s+[■]?([\d,]+\.\d+)", text),
    #     "total_debits": safe_search(r"Total Debits\s+\(-\)\s+[■]?([\d,]+\.\d+)", text),
    #     "closing_balance": safe_search(r"Closing Balance\s+[■]?([\d,]+\.\d+)", text),
    #     "total_transactions": safe_search(r"Total Transactions\s+(\d+)", text)
    # }
    return {
        "opening_balance": safe_search_number(r"Opening Balance\s*[:\-]?\s*[^\d]*([\d,]+\.\d+)", text),
        "total_credits": safe_search_number(r"Total Credits\s*\(\+\)\s*[:\-]?\s*[^\d]*([\d,]+\.\d+)", text),
        "total_debits": safe_search_number(r"Total Debits\s*\(\-\)\s*[:\-]?\s*[^\d]*([\d,]+\.\d+)", text),
        "closing_balance": safe_search_number(r"Closing Balance\s*[:\-]?\s*[^\d]*([\d,]+\.\d+)", text),
        "total_transactions": safe_search_number(r"Total Transactions\s+(\d+)", text)
    }

# -------------------------------------------------
# Parse Transactions
# -------------------------------------------------
def parse_transactions(text):
    """Extract all transaction details from the statement with categories"""
    # Updated pattern to match the actual format in the PDF
    # Format: Date | Description | Reference | Type | Debit | Credit | Balance
    pattern = re.compile(
        r"(\d{2}-\d{2}-\d{4})\s+"  # Date
        r"(.+?)\s+"  # Transaction Description (non-greedy)
        r"(\w+\d+)\s+"  # Reference Number
        r"(DR|CR)\s+"  # Transaction Type
        r"([\d,]+\.\d+)?\s*"  # Debit Amount (optional)
        r"([\d,]+\.\d+)?\s*"  # Credit Amount (optional)
        r"([\d,]+\.\d+)",  # Balance
        re.MULTILINE
    )

    rows = []
    for m in pattern.finditer(text):
        date = m.group(1)
        description = m.group(2).strip()
        reference = m.group(3)
        txn_type = m.group(4)
        debit = m.group(5) if m.group(5) else ""
        credit = m.group(6) if m.group(6) else ""
        balance = m.group(7)

        # Determine amount based on transaction type
        if txn_type == "DR":
            amount = debit if debit else ""
        else:  # CR
            amount = credit if credit else ""

        # Categorize the transaction
        category = categorize_transaction(description)
        category_display = get_category_display_name(category)

        rows.append([
            date,
            description,
            reference,
            txn_type,
            amount,
            balance,
            category_display
        ])

    return rows

# -------------------------------------------------
# Generate Category Summary
# -------------------------------------------------
def generate_category_summary(transactions):
    """Generate spending summary by category"""
    category_totals = {}

    for txn in transactions:
        # txn format: [date, description, reference, type, amount, balance, category]
        txn_type = txn[3]
        amount_str = txn[4]
        category = txn[6]

        # Only count debit transactions for spending
        if txn_type == "DR" and amount_str:
            try:
                amount = float(amount_str.replace(',', ''))
                if category not in category_totals:
                    category_totals[category] = 0.0
                category_totals[category] += amount
            except ValueError:
                continue

    # Convert to list of rows sorted by amount (descending)
    summary_rows = []
    for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        summary_rows.append([category, f"{total:,.2f}"])

    return summary_rows

# -------------------------------------------------
# Upload CSV to S3
# -------------------------------------------------
def upload_csv(folder, filename, headers, rows):
    """Upload CSV data to S3"""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)

    s3.put_object(
        Bucket=OUTPUT_BUCKET,
        Key=f"output/{folder}/{filename}",
        Body=buffer.getvalue(),
        ContentType="text/csv"
    )
    print(f"Uploaded: output/{folder}/{filename}")


# -------------------------------------------------
# Upload Data to Postgresql
# -------------------------------------------------
def upload_to_db(acc_info, pdf_name):
    # Mapping your acc_info dictionary to the database
    try:
        conn = psycopg2.connect(
            host="bankstatementanalysis.cb8amg0w4f2p.ap-south-1.rds.amazonaws.com",
            database="bankStatementAnalysis",
            user="postgres",
            password="Password#1234"
        )
        cur = conn.cursor()

        # Build the dynamic SQL insert
        columns = acc_info.keys()
        values = [acc_info[column] for column in columns]
        
        query = f"INSERT INTO account ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))}, %s)"
        
        cur.execute(query, list(values) + [pdf_name])
        conn.commit()
        print("Account Data inserted successfully!")

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()


# -------------------------------------------------
# Lambda Handler
# -------------------------------------------------
def lambda_handler(event, context):
    """Main Lambda function handler"""
    try:
        # Get S3 event details
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        # Process only PDFs
        if not key.lower().endswith(".pdf"):
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "skipped",
                    "reason": "Not a PDF file"
                })
            }

        # Extract PDF name for output files
        pdf_name = os.path.splitext(os.path.basename(key))[0]

        print(f"Processing: {key}")

        # Extract text from PDF
        text = extract_text_from_pdf(bucket, key)

        # ---------------- Account Info ----------------
        acc_info = parse_account_info(text)
        upload_csv(
            "account_info",
            f"{pdf_name}_account_info.csv",
            list(acc_info.keys()),
            [list(acc_info.values())]
        )

        # --------------- Account Summary --------------
        acc_summary = parse_account_summary(text)
        upload_csv(
            "account_summary",
            f"{pdf_name}_account_summary.csv",
            list(acc_summary.keys()),
            [list(acc_summary.values())]
        )

        # ---------------- Transactions ----------------
        transactions = parse_transactions(text)
        upload_csv(
            "transactions",
            f"{pdf_name}_transactions.csv",
            ["date", "description", "reference", "type", "amount", "balance", "category"],
            transactions
        )

        # ------------ Category Summary ----------------
        category_summary = generate_category_summary(transactions)
        upload_csv(
            "category_summary",
            f"{pdf_name}_category_summary.csv",
            ["category", "total_amount"],
            category_summary
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "pdf": key,
                "records_processed": len(transactions),
                "categories_found": len(category_summary),
                "account_holder": acc_info.get("account_holder", "Unknown"),
                "total_transactions": acc_summary.get("total_transactions", "Unknown")
            })
        }

    except Exception as e:
        print(f"Error processing {key}: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": str(e)
            })
        }

# -------------------------------------------------
# For Local Testing
# -------------------------------------------------
if __name__ == "__main__":
    # Test with a sample event
    test_event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "pdf-bucket-santhosh"},
                "object": {"key": "input/0002_Aarti_Yadhav_Statement.pdf"}
            }
        }]
    }

    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))