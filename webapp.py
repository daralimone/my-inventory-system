import streamlit as st
import streamlit as st

# ១. បង្កើតមុខងារត្រួតពិនិត្យការចូលប្រើ
def login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.title("🔐 ការចូលប្រើប្រាស់ប្រព័ន្ធ")
        
        # បង្កើតប្រអប់បញ្ចូលឈ្មោះ និងលេខកូដ
        username = st.text_input("ឈ្មោះអ្នកប្រើប្រាស់ (Username)")
        password = st.text_input("លេខកូដសម្ងាត់ (Password)", type="password")
        
        if st.button("ចូលប្រើ"):
            # អ្នកអាចប្តូរឈ្មោះ និងលេខកូដនៅត្រង់នេះ
            if username == "admin" and password == "12345":
                st.session_state["logged_in"] = True
                st.rerun() # ឱ្យវា Reload ដើម្បីបង្ហាញ App
            else:
                st.error("ឈ្មោះ ឬ លេខកូដសម្ងាត់មិនត្រឹមត្រូវ!")
        return False
    else:
        # បង្កើតប៊ូតុង Log out នៅចំហៀង (Sidebar)
        if st.sidebar.button("ចាកចេញ (Log out)"):
            st.session_state["logged_in"] = False
            st.rerun()
        return True

# ២. ហៅមុខងារ Login មកប្រើ
if login():
    # --- ដាក់កូដកម្មវិធីលក់ដូរ និងស្តុករបស់អ្នកទាំងអស់នៅខាងក្រោមនេះ ---
    st.title("🛍️ ប្រព័ន្ធគ្រប់គ្រងលក់ដូរ")
    
    # កូដបង្ហាញរបាយការណ៍ និងការលក់...
    st.write("ស្វាគមន៍មកកាន់ប្រព័ន្ធគ្រប់គ្រងរបស់អ្នក!")
import sqlite3
import pandas as pd

import streamlit as st

# ១. បង្កើតមុខងារត្រួតពិនិត្យ Password
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "1234": # អ្នកអាចដូរ "1234" ជាលេខដែលអ្នកចង់បាន
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # លុប password ចេញពី state ដើម្បីសុវត្ថិភាព
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # បង្ហាញផ្ទាំងឱ្យវាយ Password លើកដំបូង
        st.text_input("សូមបញ្ចូលលេខកូដសម្ងាត់", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # បើវាយខុស បង្ហាញសារព្រមាន
        st.text_input("លេខកូដមិនត្រឹមត្រូវ សូមព្យាយាមម្ដងទៀត", type="password", on_change=password_entered, key="password")
        st.error("😕 លេខកូដខុស!")
        return False
    else:
        return True

# ២. ប្រើប្រាស់មុខងារ Login
if check_password():
    # --- ដាក់កូដកម្មវិធីរបស់អ្នកទាំងអស់នៅទីនេះ ---
    st.title("🛍️ ប្រព័ន្ធគ្រប់គ្រងស្តុករបស់ខ្ញុំ")
    # ... កូដចាស់របស់អ្នក (កន្លែងលក់ កន្លែងបង្ហាញប្រតិបត្តិការ) ...
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