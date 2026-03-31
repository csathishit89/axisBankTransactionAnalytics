import connectionInfo

def creditDebitTotalsFetch(selected_year, selected_branch):
    cursor = None
    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        base_query = """
            SELECT 
                COALESCE(SUM(T.credit_amount),0) AS total_credit,
                COALESCE(SUM(T.debit_amount),0) AS total_debit
            FROM transaction T INNER JOIN account A on T.account_id=A.account_id
        """

        params = []

        if selected_year != "All Years":
            base_query += " WHERE EXTRACT(YEAR FROM T.transaction_date) = %s "
            params.append(selected_year)
        
        if selected_branch != "All Branch":
            base_query += " AND A.branch = %s "
            params.append(selected_branch)

        cursor.execute(base_query, tuple(params))
        result = cursor.fetchone()

        return result

    except Exception as e:
        print(f"Database error credit debit total : {e}")
        connectionInfo.get_active_connection()
        return (0, 0)

    finally:
        if cursor:
            cursor.close()