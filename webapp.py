import streamlit as st
import sqlite3
import pandas as pd

# ១. បង្កើតមុខងារតភ្ជាប់ Database
def get_data():
    conn = sqlite3.connect('business.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return df

# ២. រៀបចំផ្ទៃកម្មវិធី (UI)
st.set_page_config(page_title="ប្រព័ន្ធគ្រប់គ្រងស្តង់ដា", layout="wide")
st.title("📦 ប្រព័ន្ធគ្រប់គ្រងស្តុកទំនិញ")

# ផ្នែកបញ្ចូលទំនិញថ្មី
st.sidebar.header("➕ បញ្ចូលទំនិញថ្មី")
name = st.sidebar.text_input("ឈ្មោះទំនិញ")
qty = st.sidebar.number_input("ចំនួនក្នុងស្តុក", min_value=0)
price = st.sidebar.number_input("តម្លៃលក់ ($)", min_value=0.0)

if st.sidebar.button("រក្សាទុក"):
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, stock, price) VALUES (?, ?, ?)", (name, qty, price))
    conn.commit()
    conn.close()
    st.sidebar.success("បានបញ្ចូលជោគជ័យ!")

# ផ្នែកបង្ហាញទិន្នន័យ (ដូចក្នុង Browser)
st.subheader("📊 បញ្ជីទំនិញដែលមានស្រាប់")
df_products = get_data()
st.dataframe(df_products, use_container_width=True) # បង្ហាញជាតារាងស្អាត

# ផ្នែកក្រាហ្វិកសាមញ្ញ
if not df_products.empty:
    st.subheader("📈 ស្ថិតិស្តុក")
    st.bar_chart(data=df_products, x="name", y="stock")