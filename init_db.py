import sqlite3
from datetime import datetime
import os
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'llantas_expert.db')
def inicializar_base_de_datos():
    # Conectar a la base de datos (si no existe, SQLite la creará automáticamente)
    conn = sqlite3.connect(DB_NAME)
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
    # SEDAN - Rin 14
    ('Tornel Real',             185, 65, 14, 86,  'sedan',    'economica',         1200.00, 24),
    ('Tornel Evo',              185, 65, 14, 86,  'sedan',    'economica',         1250.00, 10),
    ('Kumho Solus',             195, 65, 14, 89,  'sedan',    'economica',         1400.00, 13),
    ('Firestone Firehawk',      195, 60, 14, 86,  'sedan',    'premium',           1650.00,  9),
    ('Yokohama A.drive',        205, 65, 14, 95,  'sedan',    'premium',           1850.00,  7),
    ('Hankook Optimo',          185, 60, 14, 82,  'sedan',    'economica',         1150.00, 15),
    ('Michelin Energy',         185, 70, 14, 88,  'sedan',    'premium',           1500.00,  8),
    # SEDAN - Rin 15
    ('Michelin Primacy',        195, 55, 15, 91,  'sedan',    'premium',          2300.00, 10),
    ('Bridgestone Ecopia',      195, 65, 15, 91,  'sedan',    'economica',         1750.00, 20),
    ('Kumho Ecsta',             205, 55, 15, 91,  'sedan',    'premium',           1900.00,  8),
    ('Bridgestone Turanza',     195, 65, 15, 91,  'sedan',    'premium',           1800.00,  9),
    ('Hankook Ventus',          205, 60, 15, 91,  'sedan',    'premium',           1750.00,  8),
    ('Yokohama BluEarth',       195, 65, 15, 91,  'sedan',    'economica',         1700.00, 11),
    ('Firestone Champion',      205, 60, 15, 94,  'sedan',    'economica',         1600.00, 12),
    ('Dunlop Enasave',          195, 65, 15, 91,  'sedan',    'premium',           1820.00,  7),
    # SEDAN - Rin 16
    ('Michelin Primacy',        205, 55, 16, 91,  'sedan',    'premium',          2450.00, 12),
    ('Bridgestone Ecopia',      205, 60, 16, 91,  'sedan',    'economica',         1780.00, 14),
    ('Goodyear Eagle',          215, 60, 16, 95,  'sedan',    'premium',           2100.00,  8),
    ('Continental TrueContact', 205, 55, 16, 91,  'sedan',    'economica',         1900.00,  3),
    # SEDAN - Rin 17
    ('Pirelli Cinturato',       205, 50, 17, 93,  'sedan',    'premium',           2800.00,  9),
    ('Michelin Pilot Sport',    215, 45, 17, 91,  'sedan',    'premium',           3200.00,  6),
    ('Goodyear Eagle',          225, 55, 17, 95,  'sedan',    'premium',           2250.00,  6),
    # SUV - Rin 16
    ('BFGoodrich All-Terrain T/A KO2',  265, 70, 16, 121, 'suv', 'alta_durabilidad', 4900.00, 8),
    ('Goodyear Wrangler Duratrac',      265, 70, 16, 120, 'suv', 'offroad', 4700.00, 8),
    ('Michelin LTX Trail',              265, 70, 16, 118, 'suv', 'premium', 5100.00, 8),
    ('Pirelli Scorpion ATR',            265, 70, 16, 119, 'suv', 'mixto', 4650.00, 8),
    ('Bridgestone Dueler A/T',          265, 70, 16, 120, 'suv', 'all_terrain', 4950.00, 8),
    ('Yokohama Geolandar A/T',          265, 70, 16, 121, 'suv', 'all_terrain', 4750.00, 8),
    ('Cooper Discoverer AT3',           265, 70, 16, 119, 'suv', 'offroad', 4500.00, 8),
    ('Toyo Open Country A/T III',       265, 70, 16, 120, 'suv', 'premium', 5000.00, 8),
    # SUV - Rin 17
    ('BFGoodrich Trail Terrain',        275, 65, 17, 115, 'suv', 'all_terrain', 5300.00, 8),
    ('Michelin Defender LTX',           275, 65, 17, 116, 'suv', 'premium', 5600.00, 8),
    ('Pirelli Scorpion Verde',          275, 65, 17, 114, 'suv', 'economica', 4800.00, 8),
    ('Goodyear Eagle Sport',            275, 65, 17, 115, 'suv', 'urbana', 4900.00, 8),
    ('Bridgestone Alenza',              275, 65, 17, 116, 'suv', 'premium', 5400.00, 8),
    ('Hankook Dynapro HP2',             275, 65, 17, 114, 'suv', 'economica', 4500.00, 8),
    ('Yokohama Geolandar X-CV',         275, 65, 17, 115, 'suv', 'premium', 5250.00, 8),
    ('Toyo Proxes ST III',              275, 65, 17, 116, 'suv', 'deportiva', 5500.00, 8),
    ('Michelin LTX',                    225, 65, 17, 102, 'suv',      'alta_durabilidad',  3800.00,  2),
    ('Goodyear Wrangler',               245, 65, 17, 111, 'suv',      'alta_durabilidad',  3600.00,  7),
    ('GOODYEAR WRANGLER HT',            265, 70, 17, 115, 'suv',      'alta_durabilidad',  4100.00,  4),
    # SUV - Rin 18
    ('Pirelli Scorpion',                235, 60, 18, 108, 'suv',      'premium',           4235.00, 10),
    ('Michelin Pilot Sport SUV',        285, 60, 18, 120, 'suv', 'deportiva', 6500.00, 8),
    ('Pirelli Scorpion Zero',           285, 60, 18, 119, 'suv', 'premium', 6200.00, 8),
    ('Continental CrossContact LX',     285, 60, 18, 118, 'suv', 'urbana', 6000.00, 8),
    ('Bridgestone Dueler H/L',          285, 60, 18, 119, 'suv', 'premium', 6100.00, 8),
    ('Goodyear EfficientGrip SUV',      285, 60, 18, 118, 'suv', 'economica', 5700.00, 8),
    ('Hankook Ventus S1 evo3 SUV',      285, 60, 18, 120, 'suv', 'deportiva', 5900.00, 8),
    ('Yokohama Advan Sport SUV',        285, 60, 18, 119, 'suv', 'deportiva', 6150.00, 8),
    ('Toyo Proxes Sport SUV',           285, 60, 18, 118, 'suv', 'premium', 6050.00, 8),
    # SUV - Rin 19
    ('Michelin Latitude',               255, 50, 19, 107, 'suv',      'premium',           5200.00,  4),
    ('Michelin PRIMACY SUV+',           225, 55, 19, 99,  'suv',      'premium',           5234.00,  5),
    ('Pirelli Scorpion',                245, 55, 19, 108, 'suv',      'premium',           4390.00,  4),
    # CAMIONETA - Rin 16
    ('BFGoodrich All-Terrain',          285, 75, 16, 122, 'camioneta','alta_durabilidad',  5200.00,  8),
    ('Mickey Thompson Baja',            315, 75, 16, 127, 'camioneta','alta_durabilidad',  7500.00,  4),
    # CAMIONETA - Rin 17
    ('BFGoodrich All-Terrain',          295, 70, 17, 122, 'camioneta','alta_durabilidad',  5350.00,  3),
    ('Pirelli Scorpion ATR',            265, 70, 17, 115, 'camioneta','premium',           4500.00,  0),  # SIN STOCK
    # CAMIONETA - Rin 18
    ('Nitto Trail Grappler',            305, 70, 18, 126, 'camioneta','alta_durabilidad',  6800.00,  5),
    ('Toyo Open Country',               275, 65, 18, 118, 'camioneta','premium',           4800.00,  6),
    # CAMIONETA - Rin 19
    ('Pirelli P Zero Corsa',            245, 35, 19, 93, 'camioneta', 'superdeportiva', 7800.00, 8),
    ('Michelin Pilot Sport Cup 2',      245, 35, 19, 93, 'camioneta', 'track', 8200.00, 8),
    ('Continental ExtremeContact',      245, 35, 19, 93, 'camioneta', 'deportiva', 7600.00, 8),
    ('Bridgestone Potenza Sport',       245, 35, 19, 93, 'camioneta', 'premium', 7900.00, 8),
    ('Yokohama Advan Apex',             245, 35, 19, 93, 'camioneta', 'track', 7700.00, 8),
    ('Toyo Proxes R888R',               245, 35, 19, 93, 'camioneta', 'track', 8100.00, 8),
    ('Nitto NT555 G2',                  245, 35, 19, 93, 'camioneta', 'street_performance', 7400.00, 8),
    ('Falken Azenis FK510',             245, 35, 19, 93, 'camioneta', 'premium', 7500.00, 8),
    ]
        cursor.executemany('''
            INSERT INTO inventario_llantas (marca, ancho, perfil, rin, indice_carga, tipo_vehiculo, categoria, precio, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', llantas_semilla)
        
        conn.commit()
        print(f"¡Éxito! Se insertaron {len(llantas_semilla)} llantas de prueba.")
    else:
        print("La base de datos ya tiene datos registrados.")

    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        print("Insertando clientes de prueba...")
        clientes_semilla = [
            ('Carlos Mendoza', '3311234567', 'carlos@email.com', 5, 1),  # frecuente
            ('Laura Pérez',    '3339876543', 'laura@email.com',  1, 0),  # nuevo
            ('Roberto García', '3321112233', 'roberto@email.com',0, 0),  # nuevo
        ]
        cursor.executemany('''
            INSERT INTO clientes (nombre, telefono, email, total_compras, es_frecuente)
            VALUES (?, ?, ?, ?, ?)
        ''', clientes_semilla)
        print(f"   {len(clientes_semilla)} clientes insertados.")

    conn.commit()
    conn.close()
    print("\n Base de datos 'llantas_expert.db' lista.")   

    conn.close()
    print("Conexión cerrada. Base de datos 'llantas_expert.db' lista.")

def get_connection():
    """Retorna una conexión reutilizable con row_factory para acceso por nombre de columna."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    inicializar_base_de_datos()