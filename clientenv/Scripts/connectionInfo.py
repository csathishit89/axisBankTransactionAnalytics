import psycopg2
import streamlit as st

@st.cache_resource
def get_connection():
    conn = psycopg2.connect(
        host="bankstatementanalysis.cb8amg0w4f2p.ap-south-1.rds.amazonaws.com",   # prefer 127.0.0.1 over "localhost" for TCP
        port=5432,
        user="postgres",
        password="Password#1234",
        dbname="bankStatementAnalysis"
    )
    return conn

def get_active_connection():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        st.cache_resource.clear()
        conn = get_connection()
    return conn