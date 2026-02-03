import sqlite3

def display_all_products():
    # ១. តភ្ជាប់ទៅកាន់ Database
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()

    # ២. ប្រើពាក្យបញ្ជា SQL "SELECT *" មានន័យថា "ជ្រើសរើសយកទាំងអស់"
    cursor.execute("SELECT * FROM products")
    
    # ទាញយកទិន្នន័យទាំងអស់មកទុកក្នុង Variable ឈ្មោះ rows
    rows = cursor.fetchall()

    print("--- បញ្ជីទំនិញក្នុងស្តុករបស់អ្នក ---")
    print("ID | ឈ្មោះទំនិញ | ចំនួន | តម្លៃ")
    print("-" * 30)

    for row in rows:
        print(f"{row[0]}  | {row[1]}  | {row[2]}  | ${row[3]}")

    conn.close()

# ដំណើរការមុខងារបង្ហាញទិន្នន័យ
display_all_products()