import streamlit as st
from init_db import inicializar_base_de_datos, get_connection
from agentes.agente_atencion import detectar_intencion
from agentes.agente_pedido import procesar_pedido, buscar_llanta
from agentes.agente_supervisor import supervisar_pedido

# Inicializar DB
inicializar_base_de_datos()

# Configuración de la página
st.set_page_config(
    page_title="LlantasPro - Sistema Experto",
    page_icon="LlantasPro",
    layout="wide"
)
st.title(" LlantasPro — Sistema Experto de Venta de Llantas")
st.markdown("---")
# Session State
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "etapa" not in st.session_state:
    st.session_state.etapa = "chat"
if "nombre_cliente" not in st.session_state:
    st.session_state.nombre_cliente = ""
if "nombre_confirmado" not in st.session_state:
    st.session_state.nombre_confirmado = False
if "rin_seleccionado" not in st.session_state:
    st.session_state.rin_seleccionado = None
if "tipo_seleccionado" not in st.session_state:
    st.session_state.tipo_seleccionado = None

def get_llantas(tipo_vehiculo=None, rin = None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM inventario_llantas WHERE 1=1"
    params = []
    if tipo_vehiculo:
        query += " AND tipo_vehiculo = ?"
        params.append(tipo_vehiculo)
    if rin:
        query += " AND rin = ?"
        params.append(rin)
    cursor.execute(query, params)
    llantas = cursor.fetchall()
    conn.close()
    return llantas

def get_rines_disponibles(tipo_vehiculo=None):
    conn = get_connection()
    cursor = conn.cursor()
    if tipo_vehiculo:
        cursor.execute("SELECT DISTINCT rin FROM inventario_llantas WHERE tipo_vehiculo = ? ORDER BY rin", (tipo_vehiculo,))
    else:
        cursor.execute("SELECT DISTINCT rin FROM inventario_llantas ORDER BY rin")
    rines = [r['rin'] for r in cursor.fetchall()]
    conn.close()
    return rines

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("LlantasPro")
    st.markdown("Sistema Experto de Venta de Llantas")
    st.markdown("---")
    st.markdown("**Tipos de vehiculo disponibles:**")
    st.markdown("- Sedan")
    st.markdown("- SUV")
    st.markdown("- Camioneta Especial")
    st.markdown("---")
    st.markdown("**Rines disponibles:** 14, 15, 16, 17, 18, 19")
    st.markdown("---")
    st.markdown("**Categorias:**")
    st.markdown("- Economica")
    st.markdown("- Premium")
    st.markdown("- Deportiva")
    st.markdown("- Urbana")
    st.markdown("- all_terrain")
    st.markdown("- Alta Durabilidad")
    
#Titulo 
st.title("LlantasPro - Sistema Experto de Venta de Llantas")
st.markdown("---")
    
# ── Chat ──────────────────────────────────────────────────────
for msg in st.session_state.mensajes:
    with st.chat_message(msg["rol"]):
        st.markdown(msg["contenido"])

# ── Etapa: Chat bienvenida ────────────────────────────────────────
if st.session_state.etapa == "bienvenida":
    bienvenida = """
Bienvenido a **LlantasPro**, tu tienda experta en llantas de alta calidad.

Contamos con una amplia variedad de llantas para todo tipo de vehiculo:

- **Sedan** — Llantas economicas y premium para tu auto compacto o familiar
- **SUV** — Llantas de alta durabilidad para terrenos variados
- **Camioneta Especial** — Llantas de alto desempeno para Jeep, Mercedes, pickup rudo y vehiculos 4x4

Manejamos rines del **14 al 19** con marcas lideres como Michelin, Bridgestone, Pirelli, Goodyear, BFGoodrich, Nitto y mas.

Escribe tu mensaje para comenzar. Puedes preguntarme sobre nuestro catalogo, disponibilidad o iniciar tu compra.
"""
    st.session_state.mensajes.append({"rol": "assistant", "contenido": bienvenida})
    with st.chat_message("assistant"):
        st.markdown(bienvenida)
    st.session_state.etapa = "chat"
    st.rerun()

# ── Etapa: Chat normal ────────────────────────────────────────
if st.session_state.etapa == "chat":
    if prompt := st.chat_input("Escribe tu mensaje..."):
        
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Analizando tu mensaje..."):
            resultado = detectar_intencion(prompt)
            
        intencion = resultado['intencion']
        respuesta = resultado['respuesta']
            
        st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})
        with st.chat_message("assistant"):
            st.markdown(respuesta)
            st.caption(f"Intencion detectada: {intencion}")
            
        if intencion in ['COMPRA', 'STOCK']:
            if not st.session_state.nombre_confirmado:
                st.session_state.etapa = "pedir_nombre"
            else:
                st.session_state.etapa = "seleccion_tipo"
            st.rerun()
            

# ── Etapa: Pedir nombre ───────────────────────────────────────
elif st.session_state.etapa == "pedir_nombre":
    msg_nombre = "Para continuar con tu pedido necesito tu nombre. Como te llamas?"
    if not any(m["contenido"] == msg_nombre for m in st.session_state.mensajes):
        st.session_state.mensajes.append({"rol": "assistant", "contenido": msg_nombre})
        with st.chat_message("assistant"):
            st.markdown(msg_nombre)
    
    if prompt := st.chat_input("Escribe tu nombre..."):
        st.session_state.nombre_cliente = prompt
        st.session_state.nombre_confirmado = True

        st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        respuesta = f"Mucho gusto, {prompt}**. Ahora selecciona el tipo de vehiculo y el rin para mostrarte las llantas disponibles."
        st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})
        with st.chat_message("assistant"):
            st.markdown(respuesta)

        st.session_state.etapa = "seleccion_tipo"
        st.rerun()
        
# ── Etapa: Selección de llanta y tipo de rin ────────────────────────────────
elif st.session_state.etapa == "seleccion_tipo":
    st.subheader(" Selecciona tu llanta")
    
    col1, col2 = st.columns(2)

    with col1:
        tipo = st.selectbox(
            "Tipo de vehiculo:",
            ["sedan", "suv", "camioneta"],
            format_func=lambda x: {"sedan": "Sedan", "suv": "SUV", "camioneta": "Camioneta Especial"}[x]
        )

    with col2:
        rines = get_rines_disponibles(tipo)
        rin = st.selectbox("Tamano de rin:", rines, format_func=lambda x: f"Rin {x}")

    llantas_filtradas = get_llantas(tipo, rin)
    disponibles = [l for l in llantas_filtradas if l['stock'] > 0]
    sin_stock = [l for l in llantas_filtradas if l['stock'] == 0]

    if disponibles:
        st.markdown(f"**Llantas disponibles para {tipo.upper()} - Rin {rin}:**")
        opciones = {
            f"{l['marca']} {l['ancho']}/{l['perfil']}R{l['rin']} | {l['categoria']} | ${l['precio']:.2f} | Stock: {l['stock']}": l['id']
            for l in disponibles
        }
        seleccion = st.selectbox("Selecciona una llanta:", list(opciones.keys()))
        cantidad = st.number_input("Cuantas llantas necesitas?", min_value=1, max_value=20, value=4)

        if st.button("Procesar pedido", type="primary"):
            llanta_id = opciones[seleccion]
            with st.spinner("Agente 2 procesando pedido e inferencias..."):
                resultado = procesar_pedido(st.session_state.nombre_cliente, llanta_id, cantidad)

            if resultado.get('exito'):
                st.success(f"Pedido procesado correctamente. Precio final: ${resultado['precio_final']:.2f} con {resultado['descuento_porcentaje']:.0f}% de descuento")
                st.session_state.etapa = "reporte"
                st.rerun()
            else:
                for inf in resultado.get('inferencias', []):
                    if inf['tipo'] == 'error':
                        st.error(f"No se puede procesar el pedido: {inf['accion']}")
                        st.info("Te gustaria ver otras opciones? Cambia el rin o tipo de vehiculo arriba.")
    else:
        st.warning(f"No hay llantas disponibles para {tipo.upper()} en Rin {rin}.")
        st.info("Prueba con otro rin o tipo de vehiculo.")

    if sin_stock:
        with st.expander("Ver llantas sin stock para este filtro"):
            for l in sin_stock:
                st.caption(f"{l['marca']} {l['ancho']}/{l['perfil']}R{l['rin']} - Sin existencias actualmente")
   
    

# ── Etapa: Reporte Supervisor ─────────────────────────────────
elif st.session_state.etapa == "reporte":
    st.subheader(" Reporte del Supervisor")

    with st.spinner(" Agente 3 generando reporte..."):
        reporte = supervisar_pedido()

    if reporte and "error" not in reporte:
        col1, col2, col3 = st.columns(3)
        col1.metric(" Precio Final", f"${reporte['precio_final']:.2f}")
        col2.metric(" Descuento", f"{reporte['descuento']:.0f}%")
        col3.metric(" Stock Restante", reporte['stock_restante'])

        st.markdown("###  Inferencias Aplicadas")
        for inf in reporte['inferencias']:
            if inf['tipo'] == 'descuento':
                st.success(f" **{inf['regla']}**: {inf['accion']}")
            elif inf['tipo'] == 'alerta':
                st.warning(f" **{inf['regla']}**: {inf['accion']}")
            else:
                st.info(f" **{inf['regla']}**: {inf['accion']}")

        st.markdown("###  Resumen del Agente Supervisor")
        st.markdown(reporte['resumen_ia'])

        st.markdown("---")
        if st.button(" Confirmar y Nueva Venta", type="primary"):
            st.session_state.etapa = "chat"
            st.session_state.mensajes = []
            st.rerun()

        if st.button(" Cancelar"):
            st.session_state.etapa = "chat"
            st.rerun()