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
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def obtener_ultimo_pedido():
    """Obtiene el último pedido registrado con toda su información."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            p.id, p.cantidad, p.precio_total, p.descuento_aplicado,
            p.estado, p.inferencias_log, p.fecha,
            c.nombre as cliente_nombre, c.es_frecuente, c.total_compras,
            l.marca, l.ancho, l.perfil, l.rin, l.precio as precio_unitario,
            l.stock as stock_actual, l.tipo_vehiculo, l.categoria
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        JOIN inventario_llantas l ON p.llanta_id = l.id
        ORDER BY p.id DESC
        LIMIT 1
    ''')
    pedido = cursor.fetchone()
    conn.close()
    return pedido

def obtener_pedido_por_id(pedido_id):
    """Obtiene un pedido específico por ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            p.id, p.cantidad, p.precio_total, p.descuento_aplicado,
            p.estado, p.inferencias_log, p.fecha,
            c.nombre as cliente_nombre, c.es_frecuente, c.total_compras,
            l.marca, l.ancho, l.perfil, l.rin, l.precio as precio_unitario,
            l.stock as stock_actual, l.tipo_vehiculo, l.categoria
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        JOIN inventario_llantas l ON p.llanta_id = l.id
        WHERE p.id = ?
    ''', (pedido_id,))
    pedido = cursor.fetchone()
    conn.close()
    return pedido

def generar_resumen_ia(pedido, inferencias):
    """Usa IA para generar un resumen explicable del pedido."""
    
    inferencias_texto = ""
    for inf in inferencias:
        inferencias_texto += f"- [{inf['tipo'].upper()}] {inf['regla']}: {inf['accion']}\n"

    prompt = f"""
Eres el agente supervisor de LlantasPro. Tu función es explicar de forma clara y profesional 
las decisiones tomadas en un pedido de llantas. Responde siempre en español.

DATOS DEL PEDIDO:
- Cliente: {pedido['cliente_nombre']}
- Cliente frecuente: {'Sí' if pedido['es_frecuente'] else 'No'} ({pedido['total_compras']} compras previas)
- Llanta: {pedido['marca']} {pedido['ancho']}/{pedido['perfil']}R{pedido['rin']}
- Categoría: {pedido['categoria']} para {pedido['tipo_vehiculo']}
- Cantidad: {pedido['cantidad']} llantas
- Precio unitario: ${pedido['precio_unitario']:.2f}
- Descuento aplicado: {pedido['descuento_aplicado']*100:.0f}%
- Precio final: ${pedido['precio_total']:.2f}
- Stock restante: {pedido['stock_actual']} unidades

INFERENCIAS APLICADAS POR EL SISTEMA:
{inferencias_texto}

Tu tarea es generar un resumen ejecutivo del pedido que:
1. Explique qué se vendió y a quién
2. Justifique cada descuento aplicado
3. Mencione alertas importantes (stock bajo, recomendaciones)
4. Solicite validación final al operador

Sé claro, conciso y profesional. Usa viñetas para las inferencias.
"""

    respuesta = cliente_ia.chat.completions.create(
        model="google/gemma-4-31b-it:free",
        messages=[{"role": "user", "content": prompt}]
    )
    return respuesta.choices[0].message.content.strip()

def supervisar_pedido(pedido_id=None):
    """
    Agente 3 — Supervisor/Explicador
    Genera resumen completo y explicación de decisiones del pedido.
    """
    # Obtener pedido
    if pedido_id:
        pedido = obtener_pedido_por_id(pedido_id)
    else:
        pedido = obtener_ultimo_pedido()

    if not pedido:
        return {"error": "No se encontró el pedido."}

    # Parsear inferencias
    inferencias = json.loads(pedido['inferencias_log']) if pedido['inferencias_log'] else []

    # Generar resumen con IA
    resumen_ia = generar_resumen_ia(pedido, inferencias)

    # Construir reporte completo
    reporte = {
        "pedido_id": pedido['id'],
        "cliente": pedido['cliente_nombre'],
        "llanta": f"{pedido['marca']} {pedido['ancho']}/{pedido['perfil']}R{pedido['rin']}",
        "cantidad": pedido['cantidad'],
        "precio_final": pedido['precio_total'],
        "descuento": pedido['descuento_aplicado'] * 100,
        "stock_restante": pedido['stock_actual'],
        "inferencias": inferencias,
        "resumen_ia": resumen_ia,
        "estado": pedido['estado']
    }

    return reporte

def imprimir_reporte(reporte):
    print("\n" + "="*60)
    print("       REPORTE SUPERVISOR - LlantasPro")
    print("="*60)
    print(f" Pedido ID:     #{reporte['pedido_id']}")
    print(f" Cliente:       {reporte['cliente']}")
    print(f" Llanta:        {reporte['llanta']}")
    print(f" Cantidad:      {reporte['cantidad']} unidades")
    print(f" Precio final:  ${reporte['precio_final']:.2f}")
    print(f"  Descuento:     {reporte['descuento']:.0f}%")
    print(f" Stock restante: {reporte['stock_restante']} unidades")
    print(f" Estado:        {reporte['estado'].upper()}")
    print("\n--- INFERENCIAS APLICADAS ---")
    for inf in reporte['inferencias']:
        emoji = "*" if inf['tipo'] == 'descuento' else "!" if inf['tipo'] == 'alerta' else "💡"
        print(f"{emoji} [{inf['regla']}]")
        print(f"   Condición: {inf['condicion']}")
        print(f"   Acción: {inf['accion']}")
    print("\n--- RESUMEN GENERADO POR IA ---")
    print(reporte['resumen_ia'])
    print("\n" + "="*60)
    print("¿Confirma este pedido? (El operador debe validar)")
    print("="*60)

if __name__ == "__main__":
    print("=== Agente 3 - Supervisor/Explicador ===\n")
    reporte = supervisar_pedido()
    if "error" in reporte:
        print(f"Error: {reporte['error']}")
    else:
        imprimir_reporte(reporte)