import connectionInfo

def categoryBasedSpendingFetch(selected_year, selected_branch):
    cursor = None
    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        base_query = """
            SELECT 
                C.category,
                COALESCE(SUM(T.debit_amount),0) AS total_spend
            FROM transaction T INNER JOIN category C on 
            T.transaction_id=C.transaction_id
            INNER JOIN account A on T.account_id=A.account_id
        """
        
        base_query += """
            WHERE T.transaction_type = 'DR'
        """

        params = []

        if selected_year != "All Years":
            base_query += " AND EXTRACT(YEAR FROM T.transaction_date) = %s "
            params.append(selected_year)
            
        if selected_branch != "All Branch":
            base_query += " AND A.branch = %s "
            params.append(selected_branch)

        base_query += """
            GROUP BY C.category
            ORDER BY total_spend DESC;
        """

        cursor.execute(base_query, tuple(params))
        result = cursor.fetchall()
        return result

    except Exception as e:
        print(f"Database error category based : {e}")
        connectionInfo.get_active_connection()
        return []

    finally:
        if cursor:
            cursor.close()