import sqlite3

conn = sqlite3.connect('llantas_expert.db')
cursor = conn.cursor()

# Le pedimos a la BD que nos muestre todo el inventario
cursor.execute("SELECT * FROM inventario_llantas")
filas = cursor.fetchall()

print("\n--- INVENTARIO ACTUAL EN LA BASE DE DATOS ---")
for fila in filas:
    print(f"ID: {fila[0]} | {fila[1]} | Medida: {fila[2]}/{fila[3]}R{fila[4]} | Stock: {fila[9]} | Precio: ${fila[8]}")

conn.close()