import connectionInfo

def managementDashboardCountFetch(branch=None):
    cursor = None

    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                -- Total Customers
                (SELECT COUNT(account_id) FROM account) AS total_customers,

                -- Total Transactions
                (SELECT COUNT(transaction_id) FROM transaction) AS total_transactions,

                -- Total Credits
                (SELECT COALESCE(SUM(credit_amount),0) 
                 FROM transaction 
                 WHERE transaction_type = 'CR') AS total_credits,

                -- Total Debits
                (SELECT COALESCE(SUM(debit_amount),0) 
                 FROM transaction
                 WHERE transaction_type = 'DR') AS total_debits,

                -- Total Deposits (same as credits if deposits are credits)
                (SELECT COALESCE(SUM(credit_amount),0) 
                 FROM transaction 
                 WHERE transaction_type = 'CR') AS total_deposits,

                -- Negative Balance %
                (
                    SELECT 
                        ROUND(
                            (COUNT(CASE WHEN balance < 0 THEN 1 END) * 100.0) 
                            / COUNT(*), 2
                        )
                    FROM transaction
                ) AS negative_balance_percent
        """
        params = []
        if branch!=None:
            query += " WHERE A.branch = %s "
            params.append(branch)
            
        cursor.execute(query)
        result = cursor.fetchone()

        if not result:   # ✅ correct empty check
            return False

        return {
            "total_customers": result[0],
            "total_transactions": result[1],
            "total_credits": result[2],
            "total_debits": result[3],
            "total_deposits": result[4],
            "negative_balance_percent": result[5]
        }


    except Exception as e:
        print(f"Database error managementDashboard : {e}")
        connectionInfo.get_active_connection()
        return False

    finally:
        if cursor:
            cursor.close()