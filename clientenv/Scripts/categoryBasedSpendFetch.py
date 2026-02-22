import connectionInfo

def categoryBasedSpendFetch(account_id):
    cursor = None

    try:
        cursor = connectionInfo.conn.cursor()

        query = """
            SELECT T.transaction_date, T.description_text, T.debit_amount, C.category, T.transaction_type FROM transaction T INNER JOIN category C on T.transaction_id=C.transaction_id WHERE T.account_id = %s and T.transaction_type='DR'
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