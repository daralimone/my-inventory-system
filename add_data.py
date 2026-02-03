import sqlite3

def add_product(name, qty, price):
    # ១. តភ្ជាប់ទៅកាន់ទូឯកសារដែលមានស្រាប់
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()

    # ២. ប្រើពាក្យបញ្ជា SQL ដើម្បីបញ្ចូលឈ្មោះទំនិញ ចំនួន និងតម្លៃ
    # សញ្ញា ? គឺសម្រាប់ការពារសុវត្ថិភាពទិន្នន័យ
    sql_command = "INSERT INTO products (name, stock, price) VALUES (?, ?, ?)"
    data = (name, qty, price)

    cursor.execute(sql_command, data)

    # ៣. រក្សាទុកការផ្លាស់ប្តូរ
    conn.commit()
    conn.close()
    print(f"✅ បានបញ្ចូល '{name}' ទៅក្នុងប្រព័ន្ធជោគជ័យ!")

# --- សាកល្បងបញ្ចូលទំនិញគំរូ ---
add_product("ទឹកក្រូច", 100, 0.5)
add_product("នំបុ័ង", 50, 1.2)