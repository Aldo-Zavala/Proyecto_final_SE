import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI
# Agregar la raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from init_db import get_connection

# Cargar la API key
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gemini.env'))

cliente_ia = OpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# ── MOTOR DE INFERENCIAS ─────────────────────────────────────────────────────

def aplicar_inferencias(cliente, llanta, cantidad):
    """
    Motor de reglas IF/THEN del sistema experto.
    Retorna lista de inferencias aplicadas y el descuento total.
    """
    inferencias = []
    descuento = 0.0

    # Regla 1 : stock insuficiente
    if llanta['stock']< cantidad:
        inferencias.append({

            "regla" : "STOCK_INSUFICIENTE",
            "condicion": f"stock ({llanta['stock']}) < cantidad solicitada ({cantidad})",
            "accion": "Pedido bloqueado. Se sugiere reabastecimiento",
            "tipo" : "error"
        })
        return inferencias, descuento, False #No se puede procesar
    
# REGLA 2: Stock bajo tras la venta
    stock_restante = llanta['stock'] - cantidad
    if stock_restante <= 3:
        inferencias.append({
            "regla": "ALERTA_STOCK_BAJO",
            "condicion": f"stock restante ({stock_restante}) <= 3 unidades",
            "accion": "Se recomienda reabastecer este producto pronto.",
            "tipo": "alerta"
        })  

 # REGLA 3: Cliente frecuente → 10% descuento
    if cliente['es_frecuente']:
        descuento += 0.10
        inferencias.append({
            "regla": "DESCUENTO_CLIENTE_FRECUENTE",
            "condicion": f"cliente '{cliente['nombre']}' tiene {cliente['total_compras']} compras previas",
            "accion": "Descuento del 10% aplicado por cliente frecuente.",
            "tipo": "descuento"
        })       
# REGLA 4: Compra de 4 o más llantas → 5% descuento adicional
    if cantidad >= 4:
        descuento += 0.05
        inferencias.append({
            "regla": "DESCUENTO_VOLUMEN",
            "condicion": f"cantidad solicitada ({cantidad}) >= 4 llantas",
            "accion": "Descuento adicional del 5% por compra de 4 o más llantas.",
            "tipo": "descuento"
        })
        # REGLA 5: Llanta de alta durabilidad para camioneta → recomendación
    if llanta['tipo_vehiculo'] == 'camioneta' and llanta['categoria'] == 'alta_durabilidad':
        inferencias.append({
            "regla": "RECOMENDACION_CAMIONETA",
            "condicion": "llanta de alta durabilidad para camioneta",
            "accion": "Llanta recomendada para uso rudo. Se sugiere revisar presión cada 2 meses.",
            "tipo": "recomendacion"
        })

    return inferencias, descuento, True  # Pedido puede procesarse


def buscar_llanta(llanta_id):
    """Busca una llanta por ID en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario_llantas WHERE id = ?", (llanta_id,))
    llanta = cursor.fetchone()
    conn.close()
    return llanta


def buscar_o_crear_cliente(nombre, telefono="", email=""):
    """Busca un cliente existente o crea uno nuevo."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes WHERE nombre = ?", (nombre,))
    cliente = cursor.fetchone()

    if not cliente:
        cursor.execute('''
            INSERT INTO clientes (nombre, telefono, email, total_compras, es_frecuente)
            VALUES (?, ?, ?, 0, 0)
        ''', (nombre, telefono, email))
        conn.commit()
        cursor.execute("SELECT * FROM clientes WHERE nombre = ?", (nombre,))
        cliente = cursor.fetchone()

    conn.close()
    return cliente


def guardar_pedido(cliente_id, llanta_id, cantidad, precio_total, descuento, inferencias):
    """Guarda el pedido en la base de datos y actualiza el stock."""
    conn = get_connection()
    cursor = conn.cursor()

    # Guardar pedido
    cursor.execute('''
        INSERT INTO pedidos (cliente_id, llanta_id, cantidad, precio_total, descuento_aplicado, estado, inferencias_log)
        VALUES (?, ?, ?, ?, ?, 'confirmado', ?)
    ''', (cliente_id, llanta_id, cantidad, precio_total, descuento, json.dumps(inferencias, ensure_ascii=False)))

    # Actualizar stock
    cursor.execute('''
        UPDATE inventario_llantas SET stock = stock - ? WHERE id = ?
    ''', (cantidad, llanta_id))

    # Actualizar total de compras del cliente
    cursor.execute('''
        UPDATE clientes SET total_compras = total_compras + 1 WHERE id = ?
    ''', (cliente_id,))

    # Actualizar si es frecuente (3 o más compras)
    cursor.execute('''
        UPDATE clientes SET es_frecuente = 1 WHERE id = ? AND total_compras >= 3
    ''', (cliente_id,))

    conn.commit()
    conn.close()


def procesar_pedido(nombre_cliente, llanta_id, cantidad):
    """
    Agente 2 — Generador de Pedido
    Procesa la solicitud, aplica inferencias y guarda el pedido.
    """
    # Buscar datos
    llanta = buscar_llanta(llanta_id)
    if not llanta:
        return {"error": "Llanta no encontrada en el inventario."}

    cliente = buscar_o_crear_cliente(nombre_cliente)

    # Aplicar motor de inferencias
    inferencias, descuento, puede_procesar = aplicar_inferencias(cliente, llanta, cantidad)

    if not puede_procesar:
        return {
            "exito": False,
            "mensaje": "No se puede procesar el pedido.",
            "inferencias": inferencias
        }

    # Calcular precios
    precio_unitario = llanta['precio']
    precio_sin_descuento = precio_unitario * cantidad
    monto_descuento = precio_sin_descuento * descuento
    precio_final = precio_sin_descuento - monto_descuento

    # Guardar en base de datos
    guardar_pedido(cliente['id'], llanta_id, cantidad, precio_final, descuento, inferencias)

    return {
        "exito": True,
        "cliente": cliente['nombre'],
        "llanta": f"{llanta['marca']} {llanta['ancho']}/{llanta['perfil']}R{llanta['rin']}",
        "cantidad": cantidad,
        "precio_unitario": precio_unitario,
        "precio_sin_descuento": precio_sin_descuento,
        "descuento_porcentaje": descuento * 100,
        "monto_descuento": monto_descuento,
        "precio_final": precio_final,
        "inferencias": inferencias
    }


if __name__ == "__main__":
    print("=== Agente 2 - Generador de Pedido ===\n")

    # Prueba 1: Cliente frecuente comprando 4 llantas
    print("PRUEBA 1: Carlos Mendoza (cliente frecuente) compra 4 llantas Michelin Primacy")
    resultado = procesar_pedido("Carlos Mendoza", 1, 4)
    print(f"Éxito: {resultado['exito']}")
    print(f"Cliente: {resultado['cliente']}")
    print(f"Llanta: {resultado['llanta']}")
    print(f"Precio sin descuento: ${resultado['precio_sin_descuento']:.2f}")
    print(f"Descuento aplicado: {resultado['descuento_porcentaje']:.0f}%")
    print(f"Precio final: ${resultado['precio_final']:.2f}")
    print("Inferencias aplicadas:")
    for inf in resultado['inferencias']:
        print(f"  [{inf['tipo'].upper()}] {inf['regla']}: {inf['accion']}")
    print("-" * 50)

    # Prueba 2: Stock insuficiente
    print("\nPRUEBA 2: Cliente nuevo intenta comprar 5 Michelin LTX (solo hay 2 en stock)")
    resultado2 = procesar_pedido("Ana Torres", 2, 5)
    print(f"Éxito: {resultado2['exito']}")
    print("Inferencias:")
    for inf in resultado2['inferencias']:
        print(f"  [{inf['tipo'].upper()}] {inf['regla']}: {inf['accion']}")
    print("-" * 50)