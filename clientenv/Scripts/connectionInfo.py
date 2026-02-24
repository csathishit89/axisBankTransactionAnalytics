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