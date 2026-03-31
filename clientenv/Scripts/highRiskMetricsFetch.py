import connectionInfo

def highRiskMetricsFetch():
    cursor = None

    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
        WITH customer_risk AS (
           SELECT 
                a.account_id,
                a.closing_balance,
                COALESCE(SUM(CASE 
                    WHEN (c.category = 'EMI' OR c.category = 'Loan') THEN t.debit_amount 
                    ELSE 0 END),0) AS total_emi,
                COALESCE(SUM(CASE 
                    WHEN t.transaction_type = 'CR' THEN t.credit_amount 
                    ELSE 0 END),0) AS total_income
            FROM account a
            LEFT JOIN transaction t
            ON a.account_id = t.account_id
            INNER JOIN category c on t.transaction_id = c.transaction_id
            GROUP BY a.account_id, a.closing_balance
        )

        SELECT
            -- High Risk Customers
            COUNT(CASE 
                WHEN (total_emi / NULLIF(total_income,0)) * 100 > 50 
                OR closing_balance < 0 
                THEN 1 END) AS high_risk_customers,

            -- Average EMI Burden Ratio
            ROUND(AVG(
                (total_emi / NULLIF(total_income,0)) * 100
            ),2) AS avg_emi_burden,

            -- NPA Risk Customers
            COUNT(CASE 
                WHEN (total_emi / NULLIF(total_income,0)) * 100 > 70
                OR closing_balance < -5000
                OR (total_income = 0 AND total_emi > 0)
                THEN 1 END) AS npa_risk_customers

        FROM customer_risk;
        """

        cursor.execute(query)
        result = cursor.fetchone()

        if result is None:
            return False

        return {
            "high_risk_customers": result[0] or 0,
            "avg_emi_burden": result[1] or 0,
            "npa_risk_customers": result[2] or 0
        }

    except Exception as e:
        print(f"Database error highRiskMetrics : {e}")
        connectionInfo.get_active_connection()
        return False

    finally:
        if cursor:
            cursor.close()