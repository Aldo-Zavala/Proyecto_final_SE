import os
import sys
from termcolor import cprint
from init_db import inicializar_base_de_datos, get_connection
from agentes.agente_atencion import detectar_intencion
from agentes.agente_pedido import procesar_pedido, buscar_llanta
from agentes.agente_supervisor import supervisar_pedido, imprimir_reporte


def buscar_llanta_por_descripcion(mensaje): #se busca la llanta mas relevante seun el mensaje del cliente
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario_llantas WHERE stock > 0")
    llantas = cursor.fetchall()
    conn.close()

    #buscar por tipo de vehiculo mencionado
    for llanta in llantas:
        if llanta["tipo_vehiculo"].lower() in mensaje.lower():
            return llanta
    # si no encuentra, retorna la primera disponible
    return llantas[0] if llantas else None
def mostrar_catalogo(): #muestra el catalogo completo de llantas
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario_llantas WHERE stock > 0")
    llantas = cursor.fetchall()
    conn.close()
    print("\n CATALOGO DE LLANTAS DISPONIBLES:")
    print("-" * 70)
    for l in llantas:
        print(f"  [{l['id']}] {l['marca']} {l['ancho']}/{l['perfil']}R{l['rin']} | "
              f"{l['tipo_vehiculo']} | {l['categoria']} | "
              f"${l['precio']:.2f} | Stock: {l['stock']}")
    print("-" * 70)

def flujo_compra(mensaje, nombre_cliente):#ejecuta el flujo completo de compra entre los 3 agentes 
    print("\n" + "="*60)
    print("SISTEMA EXPERTO - LLANTASPRO")
    print("="*60)
    # ── AGENTE 1: Atención al cliente ────────────────────────
    print("\n[AGENTE 1 - ATENCIÓN AL CLIENTE]")
    resultado_atencion = detectar_intencion(mensaje)
    print(f"Intención detectada: {resultado_atencion['intencion']}")
    print(f"Respuesta: {resultado_atencion['respuesta']}")
    # Si no es intención de compra, terminar flujo
    if resultado_atencion['intencion'] not in ['COMPRA', 'STOCK', 'CONSULTA']:
        print("Flujo finalizado - no se requiere procesar el pedido")
        return
    # ── Selección de llanta y cantidad ───────────────────────
    mostrar_catalogo()
    
    try:
        llanta_id = int(input("\n¿Qué llanta desea? (ingrese el número ID): "))
        cantidad = int(input("¿Cuántas llantas necesita?: "))
    except ValueError:
        print(" Entrada invalida")
        return
    llanta = buscar_llanta(llanta_id)
    if not llanta:
        print("Llanta no encontrada ")
        return
    print(f"\nSeleccionaste: {llanta['marca']} {llanta['ancho']}/{llanta['perfil']}R{llanta['rin']}")
    print(f"   Precio unitario: ${llanta['precio']:.2f}")
    print(f"   Stock disponible: {llanta['stock']}")

    # ── AGENTE 2: Generador de pedido ────────────────────────
    print("\n[AGENTE 2 - GENERADOR DE PEDIDO]")
    print("Procesando pedido y aplicando inferencias...")
    
    resultado_pedido = procesar_pedido(nombre_cliente, llanta_id, cantidad)
    if not resultado_pedido.get('exito'):
        print(" No se pudo procesar el pedido.")
        for inf in resultado_pedido.get('inferencias', []):
            print(f"  [{inf['tipo'].upper()}] {inf['accion']}")
        return
    print(f" Pedido procesado correctamente.")
    print(f"   Descuento aplicado: {resultado_pedido['descuento_porcentaje']:.0f}%")
    print(f"   Precio final: ${resultado_pedido['precio_final']:.2f}")

    # ── AGENTE 3: Supervisor ──────────────────────────────────
    print("\n[AGENTE 3 - SUPERVISOR/EXPLICADOR]")
    print("Generando reporte y explicación de decisiones...")
    
    reporte = supervisar_pedido()
    imprimir_reporte(reporte)


def main():
    """Punto de entrada principal del sistema."""
    print("="*60)
    print("  BIENVENIDO AL SISTEMA EXPERTO - LlantasPro")
    print("="*60)

    # Inicializar base de datos
    inicializar_base_de_datos()

    # Datos del cliente
    nombre_cliente = input("\n¿Cuál es tu nombre? : ")

    print("\nEscribe tu mensaje (o 'salir' para terminar):")

    while True:
        mensaje = input(f"\n{nombre_cliente}: ").strip()
        
        if mensaje.lower() == 'salir':
            print("\n ¡Hasta pronto! Gracias por visitar LlantasPro.")
            break
        
        if not mensaje:
            continue

        flujo_compra(mensaje, nombre_cliente)


if __name__ == "__main__":
    main()