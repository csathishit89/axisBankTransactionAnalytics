import connectionInfo

def customerDistributionFetch(selected_branch):
    cursor = None
    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
                SELECT 
                    CASE 
                        WHEN closing_balance BETWEEN 0 AND 10000 THEN 'Low Value (0-10K)'
                        WHEN closing_balance BETWEEN 10001 AND 100000 THEN 'Mass (10K-1L)'
                        WHEN closing_balance BETWEEN 100001 AND 1000000 THEN 'Affluent (1L-10L)'
                        ELSE 'HNI (>10L)'
                        END AS balance_segment,
                        COUNT(*) AS customer_count
                    FROM account
                """
        params = []

        if selected_branch != "All Branch":
            query += " WHERE branch = %s "
            params.append(selected_branch)

        query += """
            GROUP BY balance_segment
            ORDER BY customer_count DESC;
        """
        
        cursor.execute(query, tuple(params))
        result = cursor.fetchall()

        return result

    except Exception as e:
        print(f"Database error customerDistribution : {e}")
        connectionInfo.get_active_connection()
        return []

    finally:
        if cursor:
            cursor.close()