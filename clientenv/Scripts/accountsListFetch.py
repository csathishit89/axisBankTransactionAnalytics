import connectionInfo

def accountsListFetch():
    cursor = None

    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT account_number, account_name, account_type, ifsc_code, branch, customer_id, opening_balance, total_credits, total_debits, closing_balance, user_id FROM public.account 
        """

        cursor.execute(query)
        result = cursor.fetchall()

        if not result:   # ✅ correct empty check
            return False

        return result

    except Exception as e:
        print(f"Database error in Accounts Fetch: {e}")
        connectionInfo.get_active_connection()
        return False

    finally:
        if cursor:
            cursor.close()