import psycopg2
import pandas as pd
import connectionInfo

TABLE_NAME = "account"

def insert_data_from_csv(csv_url, table_name):
    try:
        cur = connectionInfo.conn.cursor()
        
        df = pd.read_csv(csv_url)
        
        insert_query = f"""
            INSERT INTO {table_name} (
                account_name, account_number, account_type, ifsc_code, 
                branch, statement_from_date, statement_to_date, customer_id, currency
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        data_to_insert = []
        for _, row in df.iterrows():
            statement_period = str(row[5])
            parts = statement_period.split('to')
            date_from = parts[0].strip() if len(parts) > 0 else None
            date_to = parts[1].strip() if len(parts) > 1 else None
            
            row_data = (
                str(row[0]), # account_name
                str(row[1]), # account_number (ensure no spaces if bigint)
                str(row[2]), # account_type
                str(row[3]), # ifsc_code
                str(row[4]), # branch
                date_from,   # statement_from_date
                date_to,     # statement_to_date
                str(row[6]), # customer_id
                str(row[7])  # currency
            )
            data_to_insert.append(row_data)

        if data_to_insert:
            cur.executemany(insert_query, data_to_insert)
            connectionInfo.conn.commit()
            print(f"✅ Successfully inserted {len(data_to_insert)} rows.")
            
    except Exception as error:
        print(f"❌ Error: {error}")
    finally:
        if connectionInfo.conn:
            cur.close()
            connectionInfo.conn.close()

CSV_URL = 'https://axis-bank-pdf-bucket.s3.ap-south-1.amazonaws.com/output/account_info/0036_Ravi_Srivastava_Statement_account_info.csv'
insert_data_from_csv(CSV_URL, TABLE_NAME)