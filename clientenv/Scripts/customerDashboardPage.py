import topHeader
import accountInfoFetch
import categoryBasedSpendFetch
import accountTransactionsFetch
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from decimal import Decimal

def customer_dashboard(st, user_id, user_name):
    topHeader.topHeader(st, user_name)
    
    if st.session_state['current_page'] == "customer_dashboard":
        if st.button("← Back to Dashboard"):
            st.session_state['current_page'] = 'Dashboard'
            st.rerun()
        
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
    period = ''
    total_txns = 0
    
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
    
    if categoryBasedSpendInformation:
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
    
    column_names = ['date', 'debit_amount', 'credit_amount', 'transaction_type', 'category']
    loadAccTransactionsDf = pd.DataFrame(loadAccountTransactions, columns=column_names)
    
    loadAccTransactionsDf["date"] = pd.to_datetime(loadAccTransactionsDf["date"])

    # Expense (Debit)
    loadAccTransactionsDf["expense"] = loadAccTransactionsDf["debit_amount"].where(
        loadAccTransactionsDf["transaction_type"] == "DR", 0
    ).abs()

    # Income (Credit)
    loadAccTransactionsDf["income"] = loadAccTransactionsDf["credit_amount"].where(
        loadAccTransactionsDf["transaction_type"] == "CR", 0
    ).abs()
        
    loadAccTransactionsDf["year_month"] = loadAccTransactionsDf["date"].dt.to_period("M")
    monthly_spend = loadAccTransactionsDf.groupby("year_month")["expense"].sum().reset_index()
    monthly_spend["year_month"] = monthly_spend["year_month"].dt.to_timestamp()
   
    loadAccTransactionsDf["year"] = loadAccTransactionsDf["date"].dt.year
    available_years = sorted(loadAccTransactionsDf["year"].dropna().unique())
    available_years = ["All Years"] + list(available_years)
    
    selected_year = st.selectbox("Select Year", available_years, index=0)
    
    filtered_df = loadAccTransactionsDf
    
    if selected_year!= 'All Years':
        filtered_df = loadAccTransactionsDf[
            loadAccTransactionsDf["year"] == selected_year
        ].copy()

        # Clean amount first
        filtered_df["debit_amount"] = (
            filtered_df["debit_amount"]
            .astype(str)
            .str.replace(",", "", regex=False)
        )

        filtered_df["debit_amount"] = pd.to_numeric(filtered_df["debit_amount"], errors="coerce")

        # Create expense column (after numeric conversion)
        # filtered_df["expense"] = filtered_df["debit_amount"].apply(lambda x: abs(x) if x < 0 else x)

        # Create year_month properly
        filtered_df["year_month"] = pd.to_datetime(filtered_df["date"]).dt.to_period("M")

        # Group by year_month
        monthly_spend = (
            filtered_df
            .groupby("year_month")["expense"]
            .sum()
            .reset_index()
        )
        monthly_spend["year_month"] = monthly_spend["year_month"].dt.to_timestamp()
        
    col1, col2 = st.columns([1, 1])
    with col1:
        # ==============================
        # Monthly Spending Trend Section
        # ==============================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="axis-title">Monthly Spending Trend</div>', unsafe_allow_html=True)
        
        plt.figure(figsize=(12,8))
        plt.plot(monthly_spend["year_month"], monthly_spend["expense"], marker='o')

        # plt.title("Monthly Spending Trend", fontsize=18, fontweight='bold')
        plt.xlabel("Month", fontsize=16)
        plt.ylabel("Total Spending", fontsize=16)
        plt.xticks(rotation=45, fontsize=14)
        plt.yticks(fontsize=14)
        plt.grid(True)

        plt.tight_layout()
        st.pyplot(plt) 
    
    with col2:
        # ==============================
        # Monthly Spending Comparison Section
        # ==============================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="axis-title">Monthly Spending Comparison</div>', unsafe_allow_html=True)
        
        plt.figure(figsize=(12,8))
        plt.bar(monthly_spend["year_month"].astype(str), monthly_spend["expense"])

        # plt.title("Monthly Spending Comparison", fontsize=18, fontweight='bold')
        plt.xlabel("Month", fontsize=16)
        plt.ylabel("Total Spending", fontsize=16)
        plt.xticks(rotation=90, fontsize=14)
        plt.yticks(fontsize=14)
        plt.tight_layout()
        st.pyplot(plt) 
    
    # Group monthly
    monthly_summary = (
        filtered_df
        .groupby("year_month")[["income", "expense"]]
        .sum()
        .reset_index()
    )

    # Convert Period → Timestamp (IMPORTANT for matplotlib)
    monthly_summary["year_month"] = monthly_summary["year_month"].dt.to_timestamp()
    
    col1, col2 = st.columns([1,1])
    with col1:
        # ==============================
        # Income vs Expense - {selected_year}
        # ==============================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="axis-title">Income vs Expense - {selected_year}</div>',
            unsafe_allow_html=True
        )
        plt.figure(figsize=(12,8))

        plt.plot(
            monthly_summary["year_month"],
            monthly_summary["income"],
            marker='o',
            label="Income"
        )

        plt.plot(
            monthly_summary["year_month"],
            monthly_summary["expense"],
            marker='o',
            label="Expense"
        )

        # plt.title(f"Income vs Expense - {selected_year}", fontsize=18, fontweight="bold")
        plt.xlabel("Month", fontsize=16)
        plt.ylabel("Amount", fontsize=16)

        plt.xticks(rotation=45, fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        st.pyplot(plt)
        
    category_spend = (
        filtered_df[filtered_df["expense"] > 0]
        .groupby("category")["expense"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    
    with col2:
        # ==============================
        # Top Category spend
        # ==============================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="axis-title">Top 10 Category spend - {selected_year}</div>',
            unsafe_allow_html=True
        )
        plt.figure(figsize=(12,8))

        plt.barh(
            category_spend["category"],
            category_spend["expense"]
        )

        # plt.title(f"Top 10 Category Spending - {selected_year}", fontsize=18, fontweight="bold")

        plt.xlabel("Total Expense", fontsize=16)
        plt.ylabel("Category", fontsize=16)
        plt.xticks(rotation=45, fontsize=14)
        plt.yticks(fontsize=14)
        plt.gca().invert_yaxis()  # Highest on top

        plt.tight_layout()
        st.pyplot(plt)
        
    # Group by category
    category_spend = filtered_df.groupby("category")["expense"].sum()

    # Sort descending
    category_spend = category_spend.sort_values(ascending=False)

    # Top 10
    top10 = category_spend.head(10)

    # Remaining as "Other"
    if len(category_spend) > 10:
        other = category_spend.iloc[10:].sum()
        top10["Other"] = other

    top10 = top10.astype(float)

    col1, col2 = st.columns([1,1])
    with col1:
        # ==============================
        # Top 10 Category Spend - {selected_year}
        # ==============================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="axis-title">Top 10 Category Spend {selected_year}</div>',
            unsafe_allow_html=True
        )
        plt.figure(figsize=(10,10))
        fig, ax = plt.subplots()

        wedges, texts, autotexts = plt.pie(
            top10,
            labels=top10.index,
            autopct='%1.1f%%',
            startangle=75,
            wedgeprops={'width':0.65},
            pctdistance=0.75   # Move % slightly outward
        )

        # Increase % font size
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_weight("bold")
                
        # ax.set_title("Top 10 Category Spend")

        st.pyplot(fig)
        
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        top10 = (
            filtered_df[filtered_df["expense"] > 0]
                .groupby("category", as_index=False)["expense"]
                .sum()
                .sort_values("expense", ascending=False)
                .head(10)
        )

        # Add "Other" category if needed
        total_categories = (
            filtered_df[filtered_df["expense"] > 0]
                .groupby("category")["expense"]
                .sum()
                .sort_values(ascending=False)
        )

        if len(total_categories) > 10:
            other_sum = total_categories.iloc[10:].sum()
            top10.loc[len(top10)] = ["Other", other_sum]

        top10["expense"] = top10["expense"].astype(float)

        fig = px.pie(
            top10,
            names="category",
            values="expense",
            hole=0.5,
        )

        fig.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>" +
                        "Amount: ₹%{value:,.0f}<br>" +
                        "Percentage: %{percent}"
        )

        fig.update_layout(
            title={
                "text": f"Top 10 Category Spend - {selected_year}",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 20}
            },
            legend_title="Category",
            height=425
        )

        st.plotly_chart(fig, use_container_width=True)

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