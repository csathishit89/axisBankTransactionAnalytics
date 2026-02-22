import connectionInfo

def accountTransactionsFetch(account_id):
    cursor = None

    try:
        cursor = connectionInfo.conn.cursor()

        query = """
            SELECT T.transaction_date, T.debit_amount FROM transaction T WHERE T.account_id = %s
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