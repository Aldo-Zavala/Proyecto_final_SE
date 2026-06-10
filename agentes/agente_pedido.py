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
    