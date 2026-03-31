import connectionInfo

def fetchAvailableBranches():
    cursor = None
    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT branch FROM account ORDER BY branch ASC;
        """

        cursor.execute(query)
        result = cursor.fetchall()
        branches = [row[0] for row in result]
        return ["All Branch"] + branches


    except Exception as e:
        print(f"Database error available branches : {e}")
        connectionInfo.get_active_connection()
        return ["All Branch"]

    finally:
        if cursor:
            cursor.close()