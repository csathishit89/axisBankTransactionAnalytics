import topHeader
import accountsListFetch
import pandas as pd

def customersListPage(st, user_name):
    topHeader.topHeader(st, user_name)
    
    if st.button("← Back to Dashboard"):
        st.session_state['current_page'] = 'Dashboard'
        st.rerun()
    
    accountsListInfo = accountsListFetch.accountsListFetch()
    
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
    
    column_names = ['Account Number', 'Account Name', 'Account Type', 'IFSC Code', 'Branch', 'Customer ID', 'Opening Balance', 'Total Credits', 'Total Debits', 'Closing Balance', 'User ID']
    
    if accountsListInfo:
        customers_df = pd.DataFrame(accountsListInfo, columns=column_names)
    
        st.subheader("🏦 Customers Bank Account Information")
        
        currency_cols = ['Opening Balance', 'Total Credits', 'Total Debits', 'Closing Balance']
        styled_df = customers_df.style.format({col: format_inr for col in currency_cols})

        # Use data_editor to make the Account Number column "Clickable"
        event = st.dataframe(
            styled_df,
            hide_index=True,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "Account Number": st.column_config.TextColumn(
                    "Account Number",
                    help="Click row to view individual dashboard"
                ),
                "Opening Balance": st.column_config.TextColumn(
                    "Opening Balance",
                    width="medium",
                ),
                "Total Credits": st.column_config.TextColumn(
                    "Total Credits",
                    width="medium",
                ),
                "Total Debits": st.column_config.TextColumn(
                    "Total Debits",
                    width="medium",
                ),
                "Closing Balance": st.column_config.TextColumn(
                    "Closing Balance",
                    width="medium",
                )
            }
        )

        # Check if a row was selected
        if event.selection.rows:
            selected_index = event.selection.rows[0]
            selected_user_id = customers_df.iloc[selected_index]['User ID']
            print(selected_user_id)
            # # Set state and switch page
            st.session_state['selected_user_id'] = selected_user_id
            st.session_state['current_page'] = "customer_dashboard"
            st.rerun()
