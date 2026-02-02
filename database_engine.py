import sqlite3

def create_system_db():
    # ១. បង្កើតការតភ្ជាប់ទៅកាន់ File business.db
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()

    # ២. បង្កើតតារាងទំនិញ (Products)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock INTEGER DEFAULT 0,
            price REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ ទូឯកសារ 'business.db' ត្រូវបានបង្កើតរួចរាល់!")

create_system_db()