import connectionInfo

def fetchAvailableYears():
    cursor = None
    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT EXTRACT(YEAR FROM transaction_date) AS year
            FROM transaction
            ORDER BY year DESC;
        """

        cursor.execute(query)
        result = cursor.fetchall()
        years = [int(row[0]) for row in result]
        return ["All Years"] + years


    except Exception as e:
        print(f"Database error available years : {e}")
        connectionInfo.get_active_connection()
        return ["All Years"]

    finally:
        if cursor:
            cursor.close()