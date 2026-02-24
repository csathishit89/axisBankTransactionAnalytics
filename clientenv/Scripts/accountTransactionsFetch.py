import connectionInfo

def accountTransactionsFetch(account_id):
    cursor = None

    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT T.transaction_date, T.debit_amount, T.credit_amount, T.transaction_type, C.category FROM transaction T INNER JOIN category C on T.transaction_id=C.transaction_id WHERE T.account_id = %s
        """

        cursor.execute(query, (account_id,))
        result = cursor.fetchall()

        if not result:   # ✅ correct empty check
            return False

        return result

    except Exception as e:
        print(f"Database error: {e}")
        return False

    finally:
        if cursor:
            cursor.close()