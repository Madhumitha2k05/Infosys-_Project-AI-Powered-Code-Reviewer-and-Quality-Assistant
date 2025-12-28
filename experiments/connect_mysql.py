import streamlit as st
import mysql.connector
import pandas as pd

# -----------------------------
# MySQL Configuration
# -----------------------------
MYSQL_CONFIG = {
    "host": "madhu",
    "port": 3306,
    "user": "root",
    "password": "Madhu@2311"
}

# -----------------------------
# MySQL Connection
# -----------------------------
def get_connection(database=None):
    cfg = MYSQL_CONFIG.copy()
    if database:
        cfg["database"] = database
    return mysql.connector.connect(**cfg)

# -----------------------------
# Fix Duplicate Column Names
# -----------------------------
def fix_duplicate_columns(df):
    new_cols = []
    seen = {}
    for col in df.columns:
        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)
    df.columns = new_cols
    return df

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="MySQL Explorer", layout="wide")
st.title("MySQL Database Explorer")

# -----------------------------
# Connect to MySQL
# -----------------------------
try:
    conn = get_connection()
    st.success("Connected to MySQL")
except Exception as e:
    st.error(f"Connection failed: {e}")
    st.stop()

cursor = conn.cursor()

# -----------------------------
# Schemas
# -----------------------------
cursor.execute("SHOW DATABASES")
schemas = [db[0] for db in cursor.fetchall()]

schema = st.selectbox("Select Schema", schemas)

# -----------------------------
# Tables & Preview
# -----------------------------
if schema:
    conn_db = get_connection(schema)
    cur = conn_db.cursor()

    cur.execute("SHOW TABLES")
    tables = [t[0] for t in cur.fetchall()]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Tables")
        table = st.selectbox("Select Table", tables)

    with col2:
        if table:
            st.subheader(f"Preview: {table} (Top 10 rows)")
            df_preview = pd.read_sql(f"SELECT * FROM {table} LIMIT 10", conn_db)
            df_preview = fix_duplicate_columns(df_preview)
            st.dataframe(df_preview, use_container_width=True)

# -----------------------------
# SQL Query Executor
# -----------------------------
st.subheader("SQL Query Executor")

query = st.text_area(
    "Write SELECT query here",
    height=150,
    placeholder="SELECT * FROM employees;"
)

if st.button("Execute Query"):
    if not query.strip().lower().startswith("select"):
        st.error("Only SELECT queries are allowed")
    else:
        try:
            df_result = pd.read_sql(query, conn_db)
            df_result = fix_duplicate_columns(df_result)

            st.success("Query executed successfully")
            st.dataframe(df_result, use_container_width=True)
        except Exception as e:
            st.error(f"Error executing query:\n{e}")

# -----------------------------
# Cleanup
# -----------------------------
cursor.close()
conn.close()

