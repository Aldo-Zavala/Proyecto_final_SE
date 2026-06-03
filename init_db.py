import sqlite3
from datetime import datetime

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
    #TABLA DE CLIENTES
    print("creando tabla de 'clientes'....")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            total_compras INTEGER DEFAULT 0,
            es_frecuente BOOLEAN DEFAULT 0, --1 si ha compradi 3+ veces
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    #TABLA DE PEDIDOS
    print("Creando tabla 'pedidos'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            llanta_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_total REAL NOT NULL,
            descuento_aplicado REAL DEFAULT 0.0,  -- % de descuento (ej: 0.10 = 10%)
            estado TEXT DEFAULT 'pendiente',       -- pendiente, confirmado, cancelado
            inferencias_log TEXT,                  -- JSON con las reglas aplicadas
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (llanta_id) REFERENCES inventario_llantas(id)
        )
    ''')
    #DATOS DE INVENTARIO
    cursor.execute("SELECT COUNT(*) FROM inventario_llantas")
    if cursor.fetchone()[0] == 0:
        print("Insertando datos semilla en el inventario...")
        llantas_semilla = [
            ('Michelin Primacy', 205, 55, 16, 91, 'sedan', 'premium', 2450.00, 12),
            ('Michelin LTX', 225, 65, 17, 102, 'suv', 'alta_durabilidad', 3800.00, 2),     # STOCK BAJO (Ideal para probar alertas)
            ('Bridgestone Ecopia', 195, 65, 15, 91, 'sedan', 'economica', 1750.00, 20),
            ('Goodyear Eagle', 215, 60, 16, 95, 'sedan', 'premium', 2100.00, 8),
            ('Pirelli Scorpion', 265, 70, 17, 115, 'camioneta', 'alta_durabilidad', 4500.00, 16),
            ('Continental TrueContact', 205, 55, 16, 91, 'sedan', 'economica', 1900.00, 3), # STOCK BAJO
            ('Tornel Real', 185, 65, 14, 86, 'sedan', 'economica', 1200.00, 24)
        ]
        cursor.executemany('''
            INSERT INTO inventario_llantas (marca, ancho, perfil, rin, indice_carga, tipo_vehiculo, categoria, precio, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', llantas_semilla)
        
        conn.commit()
        print(f"¡Éxito! Se insertaron {len(llantas_semilla)} llantas de prueba.")
    else:
        print("La base de datos ya tiene datos registrados.")

    conn.close()
    print("Conexión cerrada. Base de datos 'llantas_expert.db' lista.")

if __name__ == '__main__':
    inicializar_base_de_datos()