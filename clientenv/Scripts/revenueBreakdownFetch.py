import connectionInfo

def revenueBreakdownFetch(selected_branch):
    cursor = None
    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                C.category,
                COALESCE(SUM(T.debit_amount), 0) AS total_revenue
            FROM transaction T 
            INNER JOIN category C ON T.transaction_id = C.transaction_id
            INNER JOIN account A ON T.account_id = A.account_id
            WHERE (
                -- Standard Fees & Service Charges
                C.category IN ('Charge', 'Bank Charges', 'SMS Charges', 'ATM Fees')
                OR 
                -- Interest earned by the bank (Customer is debited)
                (C.category IN ('EMI') AND T.debit_amount > 0)
            )
        """

        params = []

        if selected_branch and selected_branch != "All Branch":
            query += " AND A.branch = %s "
            params.append(selected_branch)

        query += """
            GROUP BY C.category
            ORDER BY total_revenue DESC;
        """
            
        cursor.execute(query, tuple(params))
        result = cursor.fetchall()

        return result

    except Exception as e:
        print(f"Database error revenue breakdown : {e}")
        connectionInfo.get_active_connection()
        return []

    finally:
        if cursor:
            cursor.close()