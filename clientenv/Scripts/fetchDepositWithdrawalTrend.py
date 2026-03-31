import connectionInfo

def fetchDepositWithdrawalTrend(selected_year, selected_branch):
    cursor = None

    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        # ✅ ALWAYS define base_query first
        base_query = """
            SELECT 
                TO_CHAR(T.transaction_date, 'YYYY-MM') AS month,

                COALESCE(SUM(
                    CASE 
                        WHEN T.transaction_type = 'CR' 
                        THEN T.credit_amount 
                        ELSE 0 
                    END
                ),0) AS total_deposits,

                COALESCE(SUM(
                    CASE 
                        WHEN T.transaction_type = 'DR' 
                        THEN T.debit_amount 
                        ELSE 0 
                    END
                ),0) AS total_withdrawals

            FROM transaction T INNER JOIN account A on T.account_id=A.account_id
        """

        params = []

        if selected_year != "All Years":
            base_query += " WHERE EXTRACT(YEAR FROM T.transaction_date) = %s "
            params.append(selected_year)
        
        if selected_branch != "All Branch":
            base_query += " AND A.branch = %s "
            params.append(selected_branch)

        base_query += """
            GROUP BY TO_CHAR(transaction_date, 'YYYY-MM')
            ORDER BY month;
        """

        cursor.execute(base_query, tuple(params))
        result = cursor.fetchall()

        return result

    except Exception as e:
        print(f"Database error fetch depositWithdrawl : {e}")
        connectionInfo.get_active_connection()
        return []

    finally:
        if cursor:
            cursor.close()