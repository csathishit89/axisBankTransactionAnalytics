import connectionInfo

def expenseBreakdownFetch(selected_branch):
    cursor = None
    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                C.category,
                COALESCE(SUM(T.debit_amount),0) AS total_expense
            FROM transaction T INNER JOIN category C 
            ON T.transaction_id=C.transaction_id
            INNER JOIN account A on T.account_id=A.account_id
        """
        
        query += """
            WHERE T.transaction_type = 'DR' and C.category != 'Bank Charges'
        """
        
        params = []
        
        if selected_branch != "All Branch":
            query += " AND A.branch = %s "
            params.append(selected_branch)
            
        query += """
            GROUP BY C.category
            ORDER BY total_expense DESC;
        """
        
        # query = """
        #     SELECT 
        #         C.category,
        #         SUM(CASE 
        #             -- 1. Interest paid TO customers (Credit on their statement)
        #             WHEN C.category = 'Interest' AND T.credit_amount > 0 THEN T.credit_amount
                    
        #             -- 2. Staff Salaries (Debit from bank's operational pool)
        #             WHEN C.category = 'Salary' AND T.debit_amount > 0 THEN T.debit_amount
                    
        #             -- 3. Office Maintenance, Rent, Electricity
        #             WHEN C.category = 'Maintenance' AND T.debit_amount > 0 THEN T.debit_amount
                    
        #             ELSE 0 
        #         END) AS total_expense
        #     FROM transaction T 
        #     INNER JOIN category C ON T.transaction_id = C.transaction_id
        #     INNER JOIN account A ON T.account_id = A.account_id
        #     WHERE 1=1
        # """

        # params = []

        # if selected_branch and selected_branch != "All Branch":
        #     query += " AND A.branch = %s "
        #     params.append(selected_branch)

        # query += """
        #     GROUP BY C.category
        #     -- Only show categories that actually have expenses > 0
        #     HAVING SUM(CASE 
        #         WHEN C.category = 'Interest' AND T.credit_amount > 0 THEN T.credit_amount
        #         WHEN C.category = 'Salary' AND T.debit_amount > 0 THEN T.debit_amount
        #         WHEN C.category = 'Maintenance' AND T.debit_amount > 0 THEN T.debit_amount
        #         ELSE 0 
        #     END) > 0
        #     ORDER BY total_expense DESC;
        # """

        cursor.execute(query, tuple(params))
        result = cursor.fetchall()

        return result

    except Exception as e:
        print(f"Database error expense breakdown : {e}")
        connectionInfo.get_active_connection()
        return []

    finally:
        if cursor:
            cursor.close()