import topHeader
import managementDashboardCountFetch
import fetchDepositWithdrawalTrend
import fetchAvailableYears
import fetchAvailableBranches
import revenueBreakdownFetch
import expenseBreakdownFetch
import customerDistributionFetch
import categoryBasedSpendingFetch
import creditDebitTotalsFetch
import highRiskMetricsFetch
import branchNetProfitLoss
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


def management_dashboard(st, user_id, user_name):
    topHeader.topHeader(st, user_name)
    
    managementDashboardCountInfo = managementDashboardCountFetch.managementDashboardCountFetch()
    branchesNetProfitLossInfo = branchNetProfitLoss.branchNetProfitLoss(None)

    if managementDashboardCountInfo:
        total_customers = managementDashboardCountInfo['total_customers']
        total_deposits = managementDashboardCountInfo['total_deposits']
        total_transactions = managementDashboardCountInfo['total_transactions']
        total_credits = managementDashboardCountInfo['total_credits']
        total_debits = managementDashboardCountInfo['total_debits']
        negativeBalancePercentage = managementDashboardCountInfo['negative_balance_percent']
        high_risk_count = 0
        npa_risk_count = 0
        
        def kpi_card(title, value, key):
            if st.button(f"{title}\n{value}", key=key, use_container_width=True):
                if key == "total_customers":
                    print('on customer card click')
                    st.session_state['current_page'] = "customers_list"
                    st.rerun()
                    
                if key == "high_risk_count":
                    print('on high risk customers count click')
                    st.session_state['current_page'] = "highRiskCustomersList"
                    st.rerun()
            
        col1, col2, col3, col4 = st.columns([1,1,1,1])

        with col1:
            kpi_card("Total Customers", total_customers, "total_customers")

        with col2:
            kpi_card("Total Deposits", f"₹ {total_deposits:,.0f}", "total_deposits")

        with col3:
            kpi_card("Total Transactions", total_transactions,"total_transactions")

            
        col1, col2, col3, col4 = st.columns([1,1,1,1])
        with col1:
            kpi_card("Total Credits", f"₹ {total_credits:,.0f}","total_credits")

        with col2:
            kpi_card("Total Debits", f"₹ {total_debits:,.0f}","total_debits")

        with col3:
            kpi_card("Negative Balance %", negativeBalancePercentage,"negativeBalancePercentage")
            
        highRiskMetricsData = highRiskMetricsFetch.highRiskMetricsFetch()
        avg_emi_burden = highRiskMetricsData['avg_emi_burden']
        high_risk_count = highRiskMetricsData['high_risk_customers']
        npa_risk_count = highRiskMetricsData['npa_risk_customers']
            
        col1, col2, col3, col4 = st.columns([1,1,1,1])
        with col1:
            kpi_card("EMI Burden %", avg_emi_burden,"avg_emi_burden")

        with col2:
            kpi_card("High Risk Customers", high_risk_count,"high_risk_count")

        with col3:
            kpi_card("NPA Risk %", npa_risk_count,"npa_risk_count")
            
        years = fetchAvailableYears.fetchAvailableYears()
        fetchBranches = fetchAvailableBranches.fetchAvailableBranches()
        
        if years:
            selected_year = st.selectbox("Select Year", years, index=0)
            
            selected_branch = st.selectbox("Select Branch", fetchBranches, index=0)
            
            if selected_branch:
                branchesNetProfitLossInfo = branchNetProfitLoss.branchNetProfitLoss(selected_branch)
                
            trend_data = fetchDepositWithdrawalTrend.fetchDepositWithdrawalTrend(selected_year, selected_branch)
            credit, debit = creditDebitTotalsFetch.creditDebitTotalsFetch(selected_year, selected_branch)
            revenue_data = revenueBreakdownFetch.revenueBreakdownFetch(selected_branch)
            expense_data = expenseBreakdownFetch.expenseBreakdownFetch(selected_branch)
            spending_data = categoryBasedSpendingFetch.categoryBasedSpendingFetch(selected_year, selected_branch)
            cust_data = customerDistributionFetch.customerDistributionFetch(selected_branch)
        
            col1, col2 = st.columns([2,1])
            with col1:
                if trend_data:
                    trend_data_df = pd.DataFrame(
                        trend_data,
                        columns=["Month", "Total Deposits", "Total Withdrawals"]
                    )

                    fig = px.line(
                        trend_data_df,
                        x="Month",
                        y=["Total Deposits", "Total Withdrawals"],
                        markers=True,
                        title="Monthly Deposit vs Withdrawal Trend"
                    )

                    fig.update_layout(
                        xaxis_title="Month",
                        yaxis_title="Amount",
                        legend_title="Transaction Type",
                        template="plotly_white"
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No transaction data available.")
            
            with col2:
                if debit > 0:
                    ratio = credit / debit
                else:
                    ratio = 0

                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=ratio,
                    title={'text': f"Credit vs Debit Ratio ({selected_year})"},
                    gauge={
                        'axis': {'range': [0, 2]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 0.8], 'color': "#ff4d4d"},   # red
                            {'range': [0.8, 1], 'color': "#ffcc00"},   # yellow
                            {'range': [1, 2], 'color': "#66cc66"}      # green
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': 1
                        }
                    }
                ))

                fig.update_layout(template="plotly_white")

                st.plotly_chart(fig, use_container_width=True)
        
            col1, col2 = st.columns([1,1])
            with col1:
                if revenue_data:
                    df = pd.DataFrame(
                        revenue_data,
                        columns=["Revenue Type", "Amount"]
                    )

                    fig = px.pie(
                        df,
                        names="Revenue Type",
                        values="Amount",
                        hole=0.5,  # Donut effect
                        title="Revenue Breakdown"
                    )

                    fig.update_layout(template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No revenue data available.")
                
            
            with col2:
                if expense_data:
                    df = pd.DataFrame(
                        expense_data,
                        columns=["Expense Type", "Amount"]
                    )

                    fig = px.pie(
                        df,
                        names="Expense Type",
                        values="Amount",
                        hole=0.5,
                        title="Expense Breakdown"
                    )

                    fig.update_traces(
                        textinfo='percent',
                        textposition='inside',
                        texttemplate='%{percent:.1%}',
                    )

                    fig.update_layout(
                        template="plotly_white",
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No expense data available.")
                
            col1, col2 = st.columns([1,1])
            with col1:
                if spending_data:
                    df = pd.DataFrame(
                        spending_data,
                        columns=["Category", "Total Spend"]
                    )

                    fig = px.bar(
                        df,
                        x="Total Spend",
                        y="Category",
                        orientation="h",
                        title=f"Category Based Spending - {selected_year}"
                    )

                    fig.update_layout(
                        template="plotly_white",
                        yaxis={'categoryorder':'total ascending'}
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No spending data available.")
                
            with col2:
                if cust_data:
                    df = pd.DataFrame(cust_data, columns=["Segment", "Customer Count"])

                    fig = px.bar(
                        df,
                        x="Segment",
                        y="Customer Count",
                        title="Customer Distribution by Balance",
                        text="Customer Count"
                    )

                    fig.update_layout(
                        template="plotly_white",
                        xaxis_title="Balance Segment",
                        yaxis_title="Number of Customers"
                    )

                    fig.update_traces(textposition="outside")

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No customer data available.")
                    
                    
    column_names = ['Branch', 'Total Revenue', 'Total Expenses']
    
    def format_inr(amount):
        try:
            amount = float(amount)
            s, decimals = f"{amount:.2f}".split('.')
            
            if len(s) > 3:
                last_three = s[-3:]
                remaining = s[:-3]
                out = ""
                while len(remaining) > 2:
                    out = "," + remaining[-2:] + out
                    remaining = remaining[:-2]
                formatted_amount = remaining + out + "," + last_three
            else:
                formatted_amount = s
                
            return f"₹ {formatted_amount}.{decimals}"
        except (ValueError, TypeError):
            return amount
        
    if branchesNetProfitLossInfo:
        branchesList_df = pd.DataFrame(branchesNetProfitLossInfo, columns=column_names)

        if selected_branch=='All Branch':
            st.write("**Bank Branch - Profit / Loss - Status**")
            currency_cols = ['Total Revenue', 'Total Expenses']
            styled_df = branchesList_df.style.format({col: format_inr for col in currency_cols})
            
            st.dataframe(
                styled_df,
                hide_index=True,
                use_container_width=True)
        else:
            row = branchesNetProfitLossInfo[0]
            st.markdown("#### Branch Performance - Status")

            col1, col2 = st.columns(2)

            with col1:
                total_revenue = row[1]
                total_expenses = row[2]

                st.markdown(f"""
                <div class="card">
                    <div class="card-title">💰 Revenue & Expenses</div>
                    <div class="metric-text"><b>Total Revenue:</b> ₹{total_revenue:,.2f}</div>
                    <div class="metric-text"><b>Total Expenses:</b> ₹{total_expenses:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
 
    
    st.markdown("""
        <style>
        .kpi-card {
            background-color: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.08);
            border-top: 6px solid #861f41;
            transition: 0.3s;
        }

        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.15);
        }

        .kpi-title {
            font-size: 16px;
            color: #861f41;
            margin-bottom: 10px;
        }

        .kpi-value {
            font-size: 32px;
            font-weight: bold;
            color: #861f41;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        .card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 6px solid #4CAF50;
            margin-bottom: 15px;
        }

        .card-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .metric-text {
            font-size: 16px;
            margin: 5px 0;
        }

        </style>
        """, unsafe_allow_html=True)
            
    
    st.markdown("""
        <style>
        div.stButton > button {
            height: 110px;
            border-radius: 12px;
            background-color: white;
            color: #861f41;
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.08);
            border-top: 6px solid #861f41;
            transition: 0.3s;
            white-space: pre-line;
            text-align: center;
            line-height: 45px;
            font-size: 20px;
        }
        
        div[data-testid="stButton"] button p {
            color: #861f41;
            font-weight: bold;
            font-size: 18px;
            margin: 0; /* Streamlit p tags often have default margins */
        }

        div.stButton > button:hover {
            background-color: white;
            transform: translateY(-3px);
            color: #861f41;
        }
        </style>
        """, unsafe_allow_html=True)