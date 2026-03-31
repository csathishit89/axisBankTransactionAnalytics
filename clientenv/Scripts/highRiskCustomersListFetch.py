import connectionInfo

def highRiskCustomersListFetch():
    cursor = None
    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
        WITH customer_risk AS (
            SELECT 
                a.account_number,
                a.account_name,
                a.account_type,
                a.ifsc_code, 
                a.branch, 
                a.customer_id,
                a.opening_balance,
                a.closing_balance,
                COALESCE(SUM(CASE 
                    WHEN (c.category = 'EMI' OR c.category = 'Loan') THEN t.debit_amount 
                    ELSE 0 END), 0) AS total_emi_paid,
                COALESCE(SUM(CASE 
                    WHEN t.transaction_type = 'CR' THEN t.credit_amount 
                    ELSE 0 END), 0) AS total_income,
                a.user_id
            FROM account a
            LEFT JOIN transaction t ON a.account_id = t.account_id
            LEFT JOIN category c ON t.transaction_id = c.transaction_id
            GROUP BY a.user_id, a.account_name, a.account_number, a.account_type, a.opening_balance, a.closing_balance, a.ifsc_code, a.branch, a.customer_id
        )
        SELECT 
            account_number,
            account_name,
            account_type,
            ifsc_code, branch, customer_id,
            opening_balance,
            closing_balance,
            ROUND((total_emi_paid / NULLIF(total_income, 0)) * 100, 2) AS emi_burden_percent,
            user_id
        FROM customer_risk
        WHERE (total_emi_paid / NULLIF(total_income, 0)) * 100 > 50 
           OR closing_balance < 0
        ORDER BY emi_burden_percent DESC;
        """

        cursor.execute(query)
        return cursor.fetchall()

    except Exception as e:
        print(f"Error fetching high risk list: {e}")
        return []
    finally:
        if cursor:
            cursor.close()