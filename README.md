# axisBankTransactionAnalytics
A powerful Streamlit-based financial analytics dashboard that transforms raw Axis Bank statements into meaningful insights, trends, and visualizations.

🚀 Project Overview

Axis Bank Statement Analytics is a web application designed to help users:

Upload and analyze bank statements

Track income vs expenses

Identify spending patterns

Visualize monthly trends

Understand category-wise expenditure

Monitor financial health over time

The application provides interactive dashboards with detailed financial insights.

✨ Features
🔐 1. User Authentication

Secure login system

Personalized dashboard

Session management with logout functionality

📄 2. PDF Statement Upload

Drag & Drop or manual upload

Validates PDF format

Optional preview before processing

Upload to AWS S3 (if configured)

🏦 3. Account Information Section

Displays:

Account Holder Name

Account Number

IFSC Code

Branch

Statement Period

Currency

Customer ID

📊 4. Account Summary

Provides a quick financial snapshot:

Opening Balance

Total Credits

Total Debits

Closing Balance

Total Transactions

📈 5. Monthly Spending Trend

Line chart visualization

Identifies seasonal spikes

Detects lifestyle inflation

Year filter option

📊 6. Monthly Spending Comparison

Bar chart comparison

Month-on-month expense tracking

Clear visibility of high spending months

💰 7. Income vs Expense Analysis

Visual comparison across years

Savings gap identification

Financial stability tracking

🏷️ 8. Category-wise Spending

Pie Chart representation

Donut Chart visualization

Top 10 categories by total spend

Example categories:

Online Shopping

Investments

ATM Withdrawal

Groceries

Family Support

Credit Card Payment

Food Delivery

Fuel

Restaurants

Others

🛠️ Tech Stack

Frontend & Dashboard: Streamlit

Backend Logic: Python

Data Processing: Pandas, NumPy

Visualization: Matplotlib / Plotly

Cloud Storage (Optional): AWS S3

Authentication: Custom session-based logic

📂 Project Structure
AxisBankStatementAnalytics/
│
├── app.py
├── statementPdfUploadPage.py
├── authentication.py
├── utils/
│   ├── parser.py
│   ├── analytics.py
├── assets/
├── requirements.txt
└── README.md
⚙️ Installation
1️⃣ Clone the Repository
git clone https://github.com/your-username/axis-bank-statement-analytics.git
cd axis-bank-statement-analytics
2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run the Application
streamlit run app.py
📊 How It Works

User uploads Axis Bank statement (PDF)

PDF is parsed and transaction data extracted

Data cleaned & structured into DataFrame

Categorization logic applied

Aggregations performed (monthly, yearly, category-wise)

Interactive charts rendered
