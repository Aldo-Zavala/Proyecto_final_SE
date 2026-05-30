import sqlite3

def inicializar_base_de_datos():
    # Conectar a la base de datos (si no existe, SQLite la creará automáticamente)
    conn = sqlite3.connect('llantas_expert.db')
    cursor = conn.cursor()

    print("Creando tabla 'inventario_llantas'...")
    # Crear tabla de inventario con especificaciones técnicas detalladas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario_llantas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            ancho INTEGER NOT NULL,          -- Ej: 205 (en mm)
            perfil INTEGER NOT NULL,         -- Ej: 55 (porcentaje del ancho)
            rin INTEGER NOT NULL,            -- Ej: 16 (pulgadas)
            indice_carga INTEGER NOT NULL,   -- Ej: 91 (capacidad de peso)
            tipo_vehiculo TEXT NOT NULL,     -- sedan, suv, camioneta
            categoria TEXT NOT NULL,         -- economica, premium, alta_durabilidad
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')