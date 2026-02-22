import topHeader
import accountInfoFetch
import categoryBasedSpendFetch
import accountTransactionsFetch
import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal

def customer_dashboard(st, user_id, user_name):
    topHeader.topHeader(st, user_name)
    
    accountInformation = accountInfoFetch.accountInfoFetch(user_id)
    
    account_id = 0
    account_number = '' 
    account_holder = ''
    account_type = ''
    ifsc = ''
    branch = ''
    customer_id = ''
    currency = ''
    statement_from_date = ''
    statement_to_date = ''
    opening_balance = ''
    total_credits = ''
    total_debits = ''
    closing_balance = ''
    total_transactions = ''
    
    if accountInformation:
        for record in accountInformation:
            (
                account_id, account_number, account_holder, account_type, ifsc, branch, customer_id, currency, statement_from_date, statement_to_date, opening_balance, total_credits, total_debits, closing_balance, total_transactions
            ) = record

        if account_number:
            loadAccountTransactions = accountTransactionsFetch.accountTransactionsFetch(account_id)
            
            period = (
                    statement_from_date.strftime("%d-%m-%Y")
                    + " to "
                    + statement_to_date.strftime("%d-%m-%Y")
                )
       
        opening_balance = "₹" + str(opening_balance)
        total_credits = "₹" + str(+total_credits)
        total_debits = "₹" + str(total_debits)
        total_debits = "₹"+ str(total_debits)
        closing_balance = "₹"+ str(closing_balance)
        total_txns = round(total_transactions)
    
    # ==============================
    # Account Information Section
    # ==============================
    st.markdown('<div class="axis-title">Account Information</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="axis-box">
        <div class="axis-grid">
            <div class="axis-col">
                <div><span class="axis-label">Account Holder:</span> <span class="axis-value">{account_holder}</span></div>
                <div><span class="axis-label">Account Type:</span> <span class="axis-value">{account_type}</span></div>
                <div><span class="axis-label">Branch:</span> <span class="axis-value">{branch}</span></div>
                <div><span class="axis-label">Customer ID:</span> <span class="axis-value">{customer_id}</span></div>
            </div>
            <div class="axis-col">
                <div><span class="axis-label">Account Number:</span> <span class="axis-value">{account_number}</span></div>
                <div><span class="axis-label">IFSC Code:</span> <span class="axis-value">{ifsc}</span></div>
                <div><span class="axis-label">Statement Period:</span> <span class="axis-value">{period}</span></div>
                <div><span class="axis-label">Currency:</span> <span class="axis-value">{currency}</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])  # equal width
    
    # ---------------- LEFT COLUMN ----------------
    with col1:
        # ==============================
        # Account Summary Section
        # ==============================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="axis-title">Account Summary</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <table class="axis-summary">
            <tr class="axis-summary-header">
                <td>Opening Balance</td>
                <td style="text-align:right;">{opening_balance}</td>
            </tr>
            <tr>
                <td>Total Credits (+)</td>
                <td style="text-align:right;">{total_credits}</td>
            </tr>
            <tr>
                <td>Total Debits (-)</td>
                <td style="text-align:right;">{total_debits}</td>
            </tr>
            <tr class="axis-summary-highlight">
                <td>Closing Balance</td>
                <td style="text-align:right;">{closing_balance}</td>
            </tr>
            <tr>
                <td>Total Transactions</td>
                <td style="text-align:right;">{total_txns}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
    
    columns = ["date", "description", "amount", "category", "type"]
    categoryBasedSpendInformation = categoryBasedSpendFetch.categoryBasedSpendFetch(account_id)
    
    expense_df = pd.DataFrame(categoryBasedSpendInformation, columns=columns)
    if expense_df.empty:
        st.warning("No expense data available")
        return

    # Group by category
    category_spend = (
        expense_df
        .groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )
    
    # Sort descending
    category_spend = category_spend.sort_values(ascending=False)

    # Group small categories
    threshold = Decimal("0.03") * category_spend.sum()

    small = category_spend[category_spend < threshold]
    large = category_spend[category_spend >= threshold]

    if not small.empty:
        large["Others"] = small.sum()
    
    # Plot Pie Chart
    fig, ax = plt.subplots(figsize=(6,6))
    
    def autopct_func(pct):
        return f"{pct:.1f}%" if pct > 3 else ""   # hide small slices

    ax.pie(
        large,
        labels=large.index,
        autopct=autopct_func,
        startangle=90
    )

    # ---------------- RIGHT COLUMN ----------------
    with col2:
        # ==============================
        # Category-wise Spending Section
        # ==============================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="axis-title">Category-wise Spending</div>', unsafe_allow_html=True)

        st.pyplot(fig)
        
    column_names = ['date', 'amount']
    loadAccTransactionsDf = pd.DataFrame(loadAccountTransactions, columns=column_names)
    
    loadAccTransactionsDf["date"] = pd.to_datetime(loadAccTransactionsDf["date"])

    loadAccTransactionsDf["expense"] = loadAccTransactionsDf["amount"].apply(lambda x: abs(x) if x < 0 else x)
    loadAccTransactionsDf["year_month"] = loadAccTransactionsDf["date"].dt.to_period("M")
    monthly_spend = loadAccTransactionsDf.groupby("year_month")["expense"].sum().reset_index()
    monthly_spend["year_month"] = monthly_spend["year_month"].dt.to_timestamp()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        # ==============================
        # Monthly Spending Trend Section
        # ==============================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="axis-title">Monthly Spending Trend</div>', unsafe_allow_html=True)
        
        plt.figure(figsize=(10,6))
        plt.plot(monthly_spend["year_month"], monthly_spend["expense"], marker='o')

        plt.title("Monthly Spending Trend")
        plt.xlabel("Month")
        plt.ylabel("Total Spending")
        plt.xticks(rotation=45)
        plt.grid(True)

        plt.tight_layout()
        st.pyplot(plt) 
    
    with col2:
        # ==============================
        # Monthly Spending Comparison Section
        # ==============================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="axis-title">Monthly Spending Comparison</div>', unsafe_allow_html=True)
        
        plt.figure(figsize=(10,6))
        plt.bar(monthly_spend["year_month"].astype(str), monthly_spend["expense"])

        plt.title("Monthly Spending Comparison")
        plt.xlabel("Month")
        plt.ylabel("Total Spending")
        plt.xticks(rotation=90)

        plt.tight_layout()
        st.pyplot(plt) 

    st.markdown("""
    <style>
    /* Remove default top padding */
    .block-container {
        padding-top: 1rem;
    }

    /* Section Titles */
    .axis-title {
        font-size: 22px;
        font-weight: 700;
        color: #97144D;
        margin-bottom: 10px;
    }

    /* Account Info Box */
    .axis-box {
        border: 2px solid #97144D;
        background-color: #faf4f7;
        padding: 15px;
        border-radius: 6px;
    }
    
    .axis-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        column-gap: 100px;
    }

    .axis-col div {
        margin-bottom: 16px;
        padding: 1px;
        margin-left: 30px;
    }

    /* Labels */
    .axis-label {
        font-weight: 600;
        color: #97144D;
    }

    /* Summary Table */
    .axis-summary {
        width: 450px;
        border-collapse: collapse;
    }

    .axis-summary td {
        border: 1px solid #cfcfcf;
        padding: 8px 14px;
    }

    .axis-summary-header {
        background-color: #e6e6e6;
        font-weight: 600;
    }

    .axis-summary-highlight {
        background-color: #e7efe8;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)