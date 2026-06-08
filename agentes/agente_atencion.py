import os
from dotenv import load_dotenv
import google.generativeai as genai
from database import get_connection

# Cargar la API key del archivo .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Inicializar el modelo Gemini
modelo = genai.GenerativeModel("gemini-1.5-flash")

def obtener_catalogo():
    """Consulta el inventario actual de la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT marca, ancho, perfil, rin, tipo_vehiculo, categoria, precio, stock FROM inventario_llantas")
    llantas = cursor.fetchall()
    conn.close()

    catalogo = ""
    for l in llantas:
        catalogo += f"- {l['marca']} | {l['ancho']}/{l['perfil']}R{l['rin']} | {l['tipo_vehiculo']} | {l['categoria']} | ${l['precio']:.2f} | Stock: {l['stock']}\n"
    return catalogo

def detectar_intencion(mensaje_cliente):
    """
    Agente 1 — Atención al Cliente
    Recibe el mensaje del cliente, consulta el catálogo
    y retorna una respuesta + la intención detectada.
    """
    catalogo = obtener_catalogo()

    prompt = f"""
Eres un agente experto en venta de llantas de una tienda mexicana llamada "LlantasPro".
Eres amable, profesional y respondes siempre en español.

Este es el inventario actual de la tienda:
{catalogo}

El cliente te dice:
"{mensaje_cliente}"

Tu tarea es:
1. Detectar la intención del cliente. Puede ser una de estas:
   - CONSULTA: solo quiere información
   - COMPRA: quiere comprar llantas
   - STOCK: pregunta si hay disponibilidad
   - SALUDO: solo saluda o mensaje genérico
   - OTRO: no relacionado con llantas

2. Responder al cliente de forma amable y útil basándote en el inventario.

3. Si el cliente quiere comprar, pregúntale:
   - ¿Qué tipo de vehículo tiene? (sedan, suv, camioneta)
   - ¿Qué medida necesita? (si no la menciona)
   - ¿Cuántas llantas necesita?

Responde en este formato exacto (sin cambiar las etiquetas):
INTENCION: [la intención detectada]
RESPUESTA: [tu respuesta al cliente]
"""

    respuesta = modelo.generate_content(prompt)
    texto = respuesta.text.strip()

    # Parsear la respuesta del modelo
    intencion = "OTRO"
    respuesta_cliente = texto

    for linea in texto.split("\n"):
        if linea.startswith("INTENCION:"):
            intencion = linea.replace("INTENCION:", "").strip()
        elif linea.startswith("RESPUESTA:"):
            respuesta_cliente = linea.replace("RESPUESTA:", "").strip()

    return {
        "intencion": intencion,
        "respuesta": respuesta_cliente,
        "mensaje_original": mensaje_cliente
    }


if __name__ == "__main__":
    # Prueba rápida del agente
    print("=== Agente 1 - Atención al Cliente ===\n")
    
    mensajes_prueba = [
        "Hola, buenas tardes",
        "Necesito llantas para mi SUV",
        "Necesito llantas para mi sedan",
        "¿Tienen llantas Michelin en rin 16?",
        "Quiero comprar 4 llantas para mi sedan, ¿cuánto cuestan?"
    ]

    for msg in mensajes_prueba:
        print(f"Cliente: {msg}")
        resultado = detectar_intencion(msg)
        print(f"Intención: {resultado['intencion']}")
        print(f"Agente: {resultado['respuesta']}")
        print("-" * 50)