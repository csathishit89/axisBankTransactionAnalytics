import connectionInfo

def accountInfoFetch(user_id):
    cursor = None

    try:
        cursor = connectionInfo.conn.cursor()

        query = """
            SELECT account_id, account_number, account_name, account_type, 
                   ifsc_code, branch, customer_id, currency, 
                   statement_from_date, statement_to_date, 
                   opening_balance, total_credits, total_debits, 
                   closing_balance, total_transactions
            FROM public.account 
            WHERE user_id = %s
        """

        cursor.execute(query, (user_id,))
        result = cursor.fetchall()

        if not result:   # ✅ correct empty check
            return False

        return result

    except Exception as e:
        print(f"Database error in Accounts Fetch: {e}")
        return False

    finally:
        if cursor:
            cursor.close()