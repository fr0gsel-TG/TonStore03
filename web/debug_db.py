import sqlite3

conn = sqlite3.connect('iphones_catalog.db')
cursor = conn.cursor()

cursor.execute("SELECT model, category FROM iphones_catalog")
products = cursor.fetchall()

for product in products:
    print(product)

conn.close()
