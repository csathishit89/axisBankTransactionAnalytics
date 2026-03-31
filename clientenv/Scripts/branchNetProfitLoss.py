import connectionInfo

def branchNetProfitLoss(selected_branch=None):
    cursor = None

    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()
        
        query = """
                WITH BranchCalculations AS (
                    SELECT 
                        A.branch,
                        SUM(CASE 
                            WHEN (C.category = 'Interest' OR C.category = 'Charge' OR C.category = 'Bank Charges') 
                            AND T.debit_amount > 0 THEN T.debit_amount 
                            ELSE 0 
                        END) AS total_revenue,

                        SUM(CASE 
                            WHEN (C.category != 'Bank Charges') 
                            AND T.debit_amount > 0 THEN T.debit_amount 
                            ELSE 0 
                        END) AS total_expense
                    FROM 
                        account A
                    JOIN 
                        transaction T ON A.account_id = T.account_id
                    JOIN 
                        category C ON T.transaction_id = C.transaction_id
                """

        params = []
        if selected_branch!='All Branch':
            query += " WHERE A.branch = %s "
            params.append(selected_branch)

        query += """
                    GROUP BY 
                        A.branch
                )
                SELECT 
                    branch,
                    total_revenue,
                    total_expense AS total_expenses
                FROM 
                    BranchCalculations
                ORDER BY 
                    total_revenue DESC;
            """
        
        # 4. Execute with the params list (empty list if no branch selected)
        cursor.execute(query, params)
        result = cursor.fetchall()

        if not result:
            return False

        return result

    except Exception as e:
        print(f"Database error in Net Profit Loss check : {e}")
        conn.rollback() 
        return False

    finally:
        if cursor:
            cursor.close()