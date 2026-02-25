import psycopg2
import pandas as pd
import io # Used to treat the CSV data like a file object
import hashlib
import csv
import connectionInfo

CSV_FILE_PATH = r"C:\MAMP\htdocs\axisBankTransactionAnalytics\clientEnv\Scripts\user_credentials - loanUser.csv"
TABLE_NAME = "users"

def insert_data_from_csv(csv_path, table_name):
    """
    Connects to PostgreSQL and uses the COPY FROM method 
    to quickly upload data from a CSV file.
    """
    try:
        # Establish connection
        conn = connectionInfo.get_connection()
        cur = conn.cursor()
        
        insert_query = f"""
            INSERT INTO {table_name} (userid, username, user_password, user_role)
            VALUES (%s, %s, %s, %s)
        """
        data_to_insert = []
         
        # 2. Read the CSV file and prepare data for insertion
        with open(csv_path, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            
            for row in reader:
                password = row[2]
                secure_hash = hashlib.sha256(password.encode()).hexdigest()
                row_data = (row[0], row[1], secure_hash, row[3])
                data_to_insert.append(row_data)

        if data_to_insert:
            # 3. Execute the batch insert
            cur.executemany(insert_query, data_to_insert)
            conn.commit()
            print(f"✅ Successfully inserted {len(data_to_insert)} rows into {table_name}.")
            
    except (Exception, psycopg2.Error) as error:
        print(f"❌ Error while connecting to PostgreSQL or inserting data: {error}")
    finally:
        # Close the database connection
        if conn:
            cur.close()
            conn.close()

insert_data_from_csv(CSV_FILE_PATH, TABLE_NAME)