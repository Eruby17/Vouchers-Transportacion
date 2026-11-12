import streamlit as st
import datetime
from fpdf import FPDF
import os
import base64
import streamlit.components.v1 as components

# Streamlit Page Configuration
st.set_page_config(page_title="Corporate Travel Alliance Voucher Generator", layout="centered", page_icon="📋")

# --- LANGUAGE CONFIGURATION ---
idioma = st.sidebar.radio("🌐 Language / Idioma", ["English", "Español"], index=0)

modo_voucher = st.sidebar.radio(
    "📋 Voucher",
    ["crear", "modificar"],
    format_func=lambda opcion: (
        ("Create voucher" if idioma == "English" else "Crear voucher")
        if opcion == "crear"
        else ("Modify voucher" if idioma == "English" else "Modificar voucher")
    ),
    key="modo_voucher",
)

# Dictionary for interface translations
t = {
    "title": "📋 Transportation Voucher Creator" if idioma == "English" else "📋 Creador de Vales de Transporte",
    "desc": "Complete the service details to generate the professional executive PDF voucher." if idioma == "English" else "Complete los detalles del servicio para generar el vale en PDF ejecutivo.",
    "sub_info": "Service Information" if idioma == "English" else "Información del Servicio",
    "type": "Service Type" if idioma == "English" else "Tipo de Servicio",
    "ow_arr": "One Way (Arrival Only)" if idioma == "English" else "Sencillo (Solo Llegada)",
    "ow_dep": "One Way (Departure Only)" if idioma == "English" else "Sencillo (Solo Salida)",
    "rt": "Round Trip" if idioma == "English" else "Viaje Redondo",
    "tab_arr": "🛬 Arrival Information" if idioma == "English" else "🛬 Información de Llegada",
    "tab_dep": "🛫 Departure Information" if idioma == "English" else "🛫 Información de Salida",
    "guest": "Guest Name (UPPERCASE allowed)" if idioma == "English" else "Nombre del Huésped",
    "date_arr": "Arrival Date" if idioma == "English" else "Fecha de Llegada",
    "date_dep": "Departure Date" if idioma == "English" else "Fecha de Salida",
    "addons": "**Add-ons:**" if idioma == "English" else "**Adicionales:**",
    "cs": "Require Car Seats?" if idioma == "English" else "¿Requiere Asientos de Bebé?",
    "gs": "Include Grocery Stop?" if idioma == "English" else "¿Incluir Parada de Súper?",
    "airline_arr": "Arrival Airline" if idioma == "English" else "Aerolínea de Llegada",
    "airline_dep": "Departure Airline" if idioma == "English" else "Aerolínea de Salida",
    "airline_other": "Other airline (enter manually)" if idioma == "English" else "Otra aerolínea (escribir manualmente)",
    "airline_custom_arr": "Enter arrival airline" if idioma == "English" else "Escribe la aerolínea de llegada",
    "airline_custom_dep": "Enter departure airline" if idioma == "English" else "Escribe la aerolínea de salida",
    "err_airline": "Please enter the airline name." if idioma == "English" else "Por favor, escribe el nombre de la aerolínea",
    "time_arr": "Arrival Time" if idioma == "English" else "Hora de Llegada",
    "time_dep": "Flight Departure Time" if idioma == "English" else "Hora de Salida del Vuelo",
    "conf": "Hotel Confirmation" if idioma == "English" else "Confirmación del Hotel",
    "flight": "Flight Number" if idioma == "English" else "Número de Vuelo",
    "flight_dep": "Departure Flight Number" if idioma == "English" else "Número de Vuelo de Salida",
    "term": "Arrival Terminal" if idioma == "English" else "Terminal de Llegada",
    "pax": "**Passengers:**" if idioma == "English" else "**Pasajeros:**",
    "adults": "Adults" if idioma == "English" else "Adultos",
    "children": "Children" if idioma == "English" else "Niños",
    "custom_p": "Customize Pick-up Time Manually" if idioma == "English" else "Personalizar Hora de Recolección Manualmente",
    "p_auto": "Scheduled Pick-up Time (Auto-calculated)" if idioma == "English" else "Hora de Recolección (Auto-calculada)",
    "p_manual": "Scheduled Pick-up Time" if idioma == "English" else "Hora de Recolección Programada",
    "btn_process": "### Process and Generate" if idioma == "English" else "### Procesar y Generar",
    "btn_gen": "🚀 Generate PDF Voucher" if idioma == "English" else "🚀 Generar Vale en PDF",
    "btn_dl": "📥 Download PDF Voucher" if idioma == "English" else "📥 Descargar Vale en PDF",
    "err_name": "Please enter the guest name." if idioma == "English" else "Por favor, introduzca el nombre del huésped.",
    "err_req": "Please complete the required fields." if idioma == "English" else "Por favor, complete los campos obligatorios.",
    "err_dep": "Please enter the departure details." if idioma == "English" else "Por favor, introduzca los detalles de salida.",
    "success": "Voucher successfully generated!" if idioma == "English" else "¡Vale generado con éxito!",
    "reset": "🧹 Reset Form / Limpiar Formulario" if idioma == "English" else "🧹 Limpiar Formulario"
}

# --- LECTURA Y DATOS EDITABLES DE LOS VOUCHERS ---
# PyMuPDF sólo es necesario al cargar vouchers existentes.
import base64
import hashlib
import json
import re
import zlib

MARCADOR_VOUCHER = "CTA-VOUCHER-V1:"
AEROLINEAS_CONOCIDAS = (
    "Air Canada", "Aeroméxico", "Alaska Airlines", "American Airlines",
    "Delta Airlines", "United Airlines", "Frontier Airlines", "Jet Blue Airlines",
    "JSX", "Southwest Airlines", "Viva Aerobus", "Volaris",
    "WestJet Airlines", "Private Jet",
)
MESES_PDF = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def codificar_datos_voucher(datos):
    """Conserva datos editables dentro de los metadatos del propio PDF."""
    contenido = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return MARCADOR_VOUCHER + base64.urlsafe_b64encode(zlib.compress(contenido, 9)).decode("ascii")


def decodificar_datos_voucher(texto):
    if not texto or not texto.startswith(MARCADOR_VOUCHER):
        return None
    # Límite adicional para no procesar cargas descomprimidas enormes.
    comprimido = base64.b64decode(texto[len(MARCADOR_VOUCHER):], altchars=b"-_", validate=True)
    dec = zlib.decompressobj()
    contenido = dec.decompress(comprimido, 16000)
    if dec.unconsumed_tail or not dec.eof or len(contenido) > 16000:
        raise ValueError("Los datos del PDF exceden el tamaño permitido.")
    datos = json.loads(contenido.decode("utf-8"))
    if not isinstance(datos, dict) or datos.get("schema_version") != 1:
        raise ValueError("El formato de los datos editables no es compatible.")
    return datos


def normalizar_lineas_pdf(palabras, x_min=0, x_max=99999):
    """Reconstruye renglones por coordenadas para no mezclar las dos columnas."""
    seleccion = [p for p in palabras if x_min <= (p[0] + p[2]) / 2 < x_max]
    seleccion.sort(key=lambda p: ((p[1] + p[3]) / 2, p[0]))
    filas = []
    for p in seleccion:
        centro_y = (p[1] + p[3]) / 2
        if filas and abs(filas[-1][0] - centro_y) <= 3.5:
            filas[-1][1].append(p)
        else:
            filas.append((centro_y, [p]))
    return [" ".join(p[4] for p in sorted(fila, key=lambda item: item[0])).strip()
            for _, fila in filas]


def obtener_campo_pdf(lineas, expresiones):
    for linea in lineas:
        for expresion in expresiones:
            encontrado = re.search(expresion, linea, flags=re.IGNORECASE)
            if encontrado:
                return encontrado.group(1).strip()
    return ""


def convertir_fecha_pdf(texto):
    m = re.search(r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)\s+(\d{1,2}),?\s+(\d{4})", texto or "")
    if not m:
        return ""
    mes = MESES_PDF.get(m.group(1).casefold())
    if not mes:
        return ""
    try:
        return datetime.date(int(m.group(3)), mes, int(m.group(2))).isoformat()
    except ValueError:
        return ""


def convertir_hora_pdf(texto):
    m = re.search(r"\b(\d{1,2}):(\d{2})\s*([AP]M)?\b", texto or "", re.IGNORECASE)
    if not m:
        return ""
    hora, minuto = int(m.group(1)), int(m.group(2))
    ampm = (m.group(3) or "").upper()
    if ampm:
        if not 1 <= hora <= 12:
            return ""
        hora = (hora % 12) + (12 if ampm == "PM" else 0)
    if not (0 <= hora <= 23 and 0 <= minuto <= 59):
        return ""
    return f"{hora:02d}:{minuto:02d}"


def separar_aerolinea_vuelo(texto):
    texto = (texto or "").strip()
    if not texto:
        return "", ""
    for aerolinea in sorted(AEROLINEAS_CONOCIDAS, key=len, reverse=True):
        if texto.casefold() == aerolinea.casefold():
            return aerolinea, ""
        if texto.casefold().startswith(aerolinea.casefold() + " "):
            return aerolinea, texto[len(aerolinea):].strip()
    # Para aerolíneas manuales, el número de vuelo se infiere solamente si contiene dígitos.
    encontrado = re.match(r"^(.+?)\s+([A-Z0-9-]*\d[A-Z0-9-]*)$", texto, re.IGNORECASE)
    if encontrado:
        return encontrado.group(1).strip(), encontrado.group(2).strip()
    return texto, ""


def leer_voucher_pdf(archivo_bytes):
    """Regresa (datos, origen, advertencias). Sólo primera página del voucher."""
    if not archivo_bytes or len(archivo_bytes) > 12 * 1024 * 1024:
        raise ValueError("El archivo debe ser un PDF de máximo 12 MB.")
    if not archivo_bytes.startswith(b"%PDF-"):
        raise ValueError("El archivo no parece ser un PDF válido.")
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("Instala PyMuPDF con: pip install pymupdf") from exc

    with fitz.open(stream=archivo_bytes, filetype="pdf") as documento:
        if documento.needs_pass:
            raise ValueError("Este PDF tiene contraseña. Sube una copia sin contraseña.")
        if documento.page_count < 1:
            raise ValueError("El PDF no contiene páginas.")
        avisos = []
        try:
            datos = decodificar_datos_voucher((documento.metadata or {}).get("keywords", ""))
            if datos is not None:
                return datos, "metadatos", avisos
        except (ValueError, UnicodeError, zlib.error, json.JSONDecodeError) as exc:
            avisos.append(f"No se pudieron usar los datos integrados ({exc}); se intentará leer el texto.")

        pagina = documento[0]
        palabras = pagina.get_text("words")
        texto = pagina.get_text("text")
        if not re.search(r"TRIP SUMMARY|RESUMEN DEL VIAJE", texto, re.IGNORECASE):
            raise ValueError("No se reconoce el formato de voucher de Corporate Travel Alliance.")

        todas = normalizar_lineas_pdf(palabras)
        # Las columnas del voucher usan milímetros; PyMuPDF reporta puntos.
        mm = 72.0 / 25.4
        izquierda = normalizar_lineas_pdf(palabras, 12 * mm, 106 * mm)
        derecha = normalizar_lineas_pdf(palabras, 107 * mm, 199 * mm)

        tiene_llegada = bool(re.search(r"ARRIVING DETAILS|DETALLES DE LLEGADA", texto, re.IGNORECASE))
        tiene_retorno = bool(re.search(r"RETURNING DETAILS|DETALLES DE REGRESO", texto, re.IGNORECASE))
        tipo = "roundtrip" if tiene_llegada and tiene_retorno and not re.search(
            r"No return service requested|No se solicitó servicio de regreso", texto, re.IGNORECASE
        ) else ("arrival" if tiene_llegada else "departure")

        datos = {"schema_version": 1, "type": tipo, "guest_name": "", "confirmation": "",
                 "adults": 2, "children": 0, "csl_private": False, "car_seats": False,
                 "grocery": False, "manual_pickup": False, "arrival_airline": "",
                 "arrival_flight": "", "departure_airline": "", "departure_flight": "",
                 "arrival_date": "", "departure_date": "", "arrival_time": "12:00",
                 "departure_time": "15:00", "pickup_time": "11:30", "terminal": "Terminal 2"}

        nombre = re.search(r"Hola,\s*(.+?)!", texto, re.IGNORECASE)
        if nombre:
            datos["guest_name"] = nombre.group(1).strip()

        # En la línea del resumen aparecen los tres campos uno tras otro.
        resumen = next((linea for linea in todas if re.search(
            r"(?:Confirmation Number|No\. de Confirmación)\s*:", linea, re.IGNORECASE)), "")
        conf = re.search(
            r"(?:Confirmation Number|No\.\s*de\s*Confirmaci[oó]n)\s*:\s*(.*?)\s*"
            r"(?:Transfer Type|Tipo de Traslado)\s*:", resumen, re.IGNORECASE
        )
        if conf:
            datos["confirmation"] = conf.group(1).strip()
        pasajeros = re.search(r"(\d+)\s*Ad\.\s*/\s*(\d+)\s*(?:Ch\.|Niñ\.|Ni.?\.)", resumen, re.IGNORECASE)
        if pasajeros:
            datos["adults"], datos["children"] = int(pasajeros.group(1)), int(pasajeros.group(2))
        else:
            avisos.append("No se pudo recuperar el número de pasajeros. Verifícalo.")

        datos["car_seats"] = bool(re.search(r"Complimentary Car Seat|Asiento de Beb[eé]", texto, re.IGNORECASE))
        datos["grocery"] = bool(re.search(r"Grocery Stop|Parada de S[uú]per", texto, re.IGNORECASE))
        datos["csl_private"] = bool(re.search(r"AIRPORT PROCEDURES.*CSL PRIVATE AIRPORT", texto, re.IGNORECASE))

        def obtener_detalles(filas):
            return {
                "date_arr": obtener_campo_pdf(filas, [r"Arrival Date:\s*(.*)$", r"Fecha de Llegada:\s*(.*)$"]),
                "date_dep": obtener_campo_pdf(filas, [r"Departure Date:\s*(.*)$", r"Fecha de Salida:\s*(.*)$"]),
                "flight": obtener_campo_pdf(filas, [r"Flight & Airline:\s*(.*)$", r"Vuelo y Aerol[ií]nea:\s*(.*)$"]),
                "arrival_time": obtener_campo_pdf(filas, [r"Arrival Time:\s*(.*)$", r"Hora de Llegada:\s*(.*)$"]),
                "departure_time": obtener_campo_pdf(filas, [r"Flight Time:\s*(.*)$", r"Hora del Vuelo:\s*(.*)$"]),
                "pickup": obtener_campo_pdf(filas, [r"Hotel Pick-up:\s*(.*)$", r"Pick-up en Hotel:\s*(.*)$"]),
                "terminal": obtener_campo_pdf(filas, [r"Location / Terminal:\s*(.*)$", r"Lugar / Terminal:\s*(.*)$"]),
            }

        if tipo == "departure":
            detalle_dep = obtener_detalles(todas)
        else:
            detalle_arr = obtener_detalles(izquierda)
            datos["arrival_date"] = convertir_fecha_pdf(detalle_arr["date_arr"])
            datos["arrival_time"] = convertir_hora_pdf(detalle_arr["arrival_time"]) or "12:00"
            datos["arrival_airline"], datos["arrival_flight"] = separar_aerolinea_vuelo(detalle_arr["flight"])
            datos["terminal"] = detalle_arr["terminal"] or "Terminal 2"
            if "CSL Private Airport" in datos["terminal"]:
                datos["csl_private"] = True
            detalle_dep = obtener_detalles(derecha) if tipo == "roundtrip" else {}

        if detalle_dep:
            datos["departure_date"] = convertir_fecha_pdf(detalle_dep["date_dep"])
            datos["departure_time"] = convertir_hora_pdf(detalle_dep["departure_time"]) or "15:00"
            datos["departure_airline"], datos["departure_flight"] = separar_aerolinea_vuelo(detalle_dep["flight"])
            pickup = convertir_hora_pdf(detalle_dep["pickup"])
            if pickup:
                datos["pickup_time"] = pickup
                # El PDF antiguo no distinguía hora manual de automática.
                # Se usa manual para evitar modificar accidentalmente la hora original.
                datos["manual_pickup"] = True

        for campo, etiqueta in (("guest_name", "nombre"), ("confirmation", "confirmación")):
            if not datos[campo]:
                avisos.append(f"No se identificó la {etiqueta}; complétala antes de generar el PDF.")
        if tipo != "departure" and not datos["arrival_date"]:
            avisos.append("Verifica la fecha de llegada: no pudo extraerse del PDF.")
        if tipo != "arrival" and not datos["departure_date"]:
            avisos.append("Verifica la fecha de salida: no pudo extraerse del PDF.")
        if tipo == "departure":
            avisos.append("En PDFs antiguos de solo salida no es posible deducir el aeropuerto privado; verifica esa casilla.")
        avisos.append("PDF antiguo: revisa los datos recuperados antes de generar la nueva versión.")
        return datos, "texto", avisos


def aplicar_datos_voucher(datos, idioma_actual):
    """Precarga los widgets ANTES de que el formulario sea construido."""
    opciones = list(AEROLINEAS_CONOCIDAS)
    otro = "Other airline (enter manually)" if idioma_actual == "English" else "Otra aerolínea (escribir manualmente)"
    tipo = datos.get("type", "arrival")
    if tipo not in ("arrival", "departure", "roundtrip"):
        tipo = "arrival"
    st.session_state["tipo_viaje_code"] = tipo
    st.session_state["guest_name"] = str(datos.get("guest_name", ""))[:200]
    st.session_state["conf_num"] = str(datos.get("confirmation", ""))[:150]
    st.session_state["fl_arr"] = str(datos.get("arrival_flight", ""))[:100]
    st.session_state["fl_dep"] = str(datos.get("departure_flight", ""))[:100]
    st.session_state["cs_check"] = bool(datos.get("car_seats", False))
    st.session_state["gs_check"] = bool(datos.get("grocery", False))
    st.session_state["csl_private"] = bool(datos.get("csl_private", False))
    st.session_state["adults_count"] = max(1, min(99, int(datos.get("adults", 2))))
    st.session_state["children_count"] = max(0, min(99, int(datos.get("children", 0))))

    for campo_estado, campo_datos, predeterminado in (
        ("date_arr_val", "arrival_date", datetime.date.today()),
        ("date_dep_val", "departure_date", datetime.date.today() + datetime.timedelta(days=4)),
    ):
        try:
            st.session_state[campo_estado] = datetime.date.fromisoformat(datos[campo_datos])
        except (KeyError, TypeError, ValueError):
            st.session_state[campo_estado] = predeterminado

    st.session_state["time_arr_val"] = convertir_hora_pdf(str(datos.get("arrival_time") or "")) or "12:00"
    st.session_state["time_dep_val"] = convertir_hora_pdf(str(datos.get("departure_time") or "")) or "15:00"
    st.session_state["custom_pickup"] = bool(datos.get("manual_pickup", False))
    st.session_state["pickup_manual"] = convertir_hora_pdf(str(datos.get("pickup_time") or "")) or "11:30"
    st.session_state["terminal_arr"] = "Terminal 1" if datos.get("terminal") == "Terminal 1" else "Terminal 2"

    aerolinea_arr = str(datos.get("arrival_airline", "")).strip()
    aerolinea_dep = str(datos.get("departure_airline", "")).strip()
    seleccion_arr = aerolinea_arr if aerolinea_arr in opciones else otro
    seleccion_dep = aerolinea_dep if aerolinea_dep in opciones else otro
    # Evitar que valores de un voucher anterior contaminen los selectores dinámicos.
    for clave in list(st.session_state.keys()):
        if clave.startswith("air_dep_"):
            del st.session_state[clave]
    st.session_state["air_arr"] = seleccion_arr
    st.session_state["air_arr_custom"] = "" if seleccion_arr != otro else aerolinea_arr
    st.session_state["air_dep_standalone"] = seleccion_dep
    st.session_state[f"air_dep_{seleccion_arr}"] = seleccion_dep
    st.session_state["air_dep_custom"] = "" if seleccion_dep != otro else aerolinea_dep

# --- SESSION STATE & RESET ---
if "guest_name" not in st.session_state:
    st.session_state["guest_name"] = ""
if "conf_num" not in st.session_state:
    st.session_state["conf_num"] = ""
if "fl_arr" not in st.session_state:
    st.session_state["fl_arr"] = ""
if "fl_dep" not in st.session_state:
    st.session_state["fl_dep"] = ""
if "air_arr_custom" not in st.session_state:
    st.session_state["air_arr_custom"] = ""
if "air_dep_custom" not in st.session_state:
    st.session_state["air_dep_custom"] = ""
if "cs_check" not in st.session_state:
    st.session_state["cs_check"] = False
if "gs_check" not in st.session_state:
    st.session_state["gs_check"] = False
if "adults_count" not in st.session_state:
    st.session_state["adults_count"] = 2
if "children_count" not in st.session_state:
    st.session_state["children_count"] = 0
if "time_arr_val" not in st.session_state:
    st.session_state["time_arr_val"] = "12:00"
if "time_dep_val" not in st.session_state:
    st.session_state["time_dep_val"] = "15:00"
if "date_arr_val" not in st.session_state:
    st.session_state["date_arr_val"] = datetime.date.today()
if "date_dep_val" not in st.session_state:
    st.session_state["date_dep_val"] = datetime.date.today() + datetime.timedelta(days=4)

def reset_form():
    st.session_state["guest_name"] = ""
    st.session_state["conf_num"] = ""
    st.session_state["fl_arr"] = ""
    st.session_state["fl_dep"] = ""
    st.session_state["air_arr_custom"] = ""
    st.session_state["air_dep_custom"] = ""
    st.session_state["cs_check"] = False
    st.session_state["gs_check"] = False
    st.session_state["adults_count"] = 2
    st.session_state["children_count"] = 0
    st.session_state["time_arr_val"] = "12:00"
    st.session_state["time_dep_val"] = "15:00"
    st.session_state["date_arr_val"] = datetime.date.today()
    st.session_state["date_dep_val"] = datetime.date.today() + datetime.timedelta(days=4)
    st.session_state["tipo_viaje_code"] = "arrival"
    st.session_state["custom_pickup"] = False
    st.session_state["pickup_manual"] = "11:30"
    st.session_state["terminal_arr"] = "Terminal 2"
    st.session_state["pdf_generado"] = None
    st.session_state["pdf_generado_datos"] = None
    st.session_state["pdf_origen_hash"] = None
    st.session_state["pdf_origen_nombre"] = None
    st.session_state["aviso_carga"] = None
    for clave in list(st.session_state.keys()):
        if clave.startswith("air_dep_") or clave == "air_arr":
            del st.session_state[clave]

# La carga ocurre antes de crear los widgets del formulario. Así se pueden precargar.
if modo_voucher == "modificar":
    pdf_subido = st.sidebar.file_uploader(
        "📎 Upload original PDF / Adjuntar PDF original",
        type=["pdf"],
        key="pdf_subido",
        help="PDF generado por Corporate Travel Alliance, nuevo o antiguo.",
    )
    if st.sidebar.button(
        "📂 Load voucher data" if idioma == "English" else "📂 Cargar datos del voucher",
        disabled=pdf_subido is None,
        use_container_width=True,
    ):
        try:
            contenido_pdf = pdf_subido.getvalue()
            datos_importados, metodo_lectura, advertencias = leer_voucher_pdf(contenido_pdf)
            aplicar_datos_voucher(datos_importados, idioma)
            st.session_state["pdf_origen_hash"] = hashlib.sha256(contenido_pdf).hexdigest()
            st.session_state["pdf_origen_nombre"] = pdf_subido.name
            st.session_state["aviso_carga"] = {
                "metodo": metodo_lectura,
                "advertencias": advertencias,
            }
            st.session_state["pdf_generado"] = None
            st.session_state["pdf_generado_datos"] = None
            st.rerun()
        except Exception as exc:
            st.sidebar.error(f"Could not load PDF: {exc}" if idioma == "English"
                             else f"No se pudo cargar el PDF: {exc}")

    if st.session_state.get("aviso_carga"):
        info = st.session_state["aviso_carga"]
        st.sidebar.success("Voucher loaded. Review the form." if idioma == "English"
                           else "Voucher cargado. Revisa los datos del formulario.")
        for advertencia in info["advertencias"]:
            st.sidebar.warning(advertencia)
        if pdf_subido is not None and st.session_state.get("pdf_origen_hash") != hashlib.sha256(pdf_subido.getvalue()).hexdigest():
            st.sidebar.info("Click Load voucher data for this PDF."
                            if idioma == "English" else "Pulsa Cargar datos para este nuevo PDF.")

# Mantener disponible la opción de aeropuerto privado en ambos modos.
csl_private = st.sidebar.checkbox(
    "🛩️ CSL Private Airport / Aeropuerto Privado CSL", value=False, key="csl_private"
)
st.sidebar.button(t["reset"], on_click=reset_form, use_container_width=True)

if modo_voucher == "modificar":
    st.title("✏️ Modify voucher" if idioma == "English" else "✏️ Modificar voucher")
    st.write("Upload a PDF in the sidebar, load its details, edit and regenerate it."
             if idioma == "English"
             else "Adjunta el PDF en la barra lateral, carga sus datos, edítalos y genera el voucher corregido.")
    if not st.session_state.get("pdf_origen_hash"):
        st.info("Select a PDF and click Load voucher data in the sidebar."
                if idioma == "English"
                else "Selecciona un PDF y haz clic en Cargar datos del voucher en la barra lateral.")
else:
    st.title(t["title"])
    st.write(t["desc"])

# --- STATIC FILES ---
LOGO_DEFAULT_PATH = "logo.jpeg"
CARTEL_PATH = "cartel.png"
logo_a_usar = LOGO_DEFAULT_PATH if os.path.exists(LOGO_DEFAULT_PATH) else None

# --- MAIN FORM ---
st.subheader(t["sub_info"])

tipo_viaje_code = st.radio(
    t["type"], ["arrival", "departure", "roundtrip"], horizontal=True,
    format_func=lambda opcion: {
        "arrival": t["ow_arr"], "departure": t["ow_dep"], "roundtrip": t["rt"]
    }[opcion],
    key="tipo_viaje_code",
)
tipo_viaje = {
    "arrival": t["ow_arr"], "departure": t["ow_dep"], "roundtrip": t["rt"]
}[tipo_viaje_code]

# Aerolíneas disponibles y opción para ingresar una no incluida en la lista.
lista_aerolineas = ["Air Canada", "Aeroméxico", "Alaska Airlines", "American Airlines", "Delta Airlines", "United Airlines", "Frontier Airlines", "Jet Blue Airlines", "JSX", "Southwest Airlines", "Viva Aerobus", "Volaris", "WestJet Airlines", "Private Jet", t["airline_other"]]

# Crear pestañas dependiendo de la selección
if tipo_viaje == t["rt"]:
    tab1, tab2 = st.tabs([t["tab_arr"], t["tab_dep"]])
elif tipo_viaje == t["ow_arr"]:
    tab1 = st.tabs([t["tab_arr"]])[0]
else:
    tab2 = st.tabs([t["tab_dep"]])[0]

# --- VARIABLES POR DEFECTO ---
nombre_huesped = ""
fecha_llegada = datetime.date.today()
vuelo_llegada_completo = ""
hora_llegada = datetime.time(12, 0)
terminal_seleccionada = "CSL Private Airport" if csl_private else "Terminal 2"
adultos = 2
ninos = 0
requiere_car_seats = False
requiere_grocery = False
confirmacion = ""
aerolinea_llegada = ""
num_vuelo_llegada = ""
aerolinea_salida = ""
num_vuelo_salida = ""
custom_pickup = False

# --- TAB LLEGADA ---
if tipo_viaje in [t["ow_arr"], t["rt"]]:
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            nombre_input = st.text_input(t["guest"], key="guest_name")
            nombre_huesped = nombre_input.strip().title()
            fecha_llegada = st.date_input(t["date_arr"], key="date_arr_val")
            
            st.write(t["addons"])
            requiere_car_seats = st.checkbox(t["cs"], key="cs_check")
            requiere_grocery = st.checkbox(t["gs"], key="gs_check")
        
        with col2:
            seleccion_aerolinea_llegada = st.selectbox(t["airline_arr"], lista_aerolineas, key="air_arr")
            if seleccion_aerolinea_llegada == t["airline_other"]:
                aerolinea_llegada = st.text_input(t["airline_custom_arr"], key="air_arr_custom").strip()
            else:
                aerolinea_llegada = seleccion_aerolinea_llegada
            hora_llegada_str = st.text_input(t["time_arr"], key="time_arr_val")
            try:
                h_arr, m_arr = map(int, hora_llegada_str.split(":"))
                hora_llegada = datetime.time(h_arr, m_arr)
            except ValueError:
                st.error("Invalid Arrival Time format. Using 12:00 as fallback.")
                hora_llegada = datetime.time(12, 0)
                
            confirmacion = st.text_input(t["conf"], key="conf_num").upper()

        with col3:
            num_vuelo_llegada = st.text_input(t["flight"], key="fl_arr")
            if csl_private:
                terminal_seleccionada = "CSL Private Airport"
            else:
                terminal_seleccionada = st.selectbox(t["term"], ["Terminal 2", "Terminal 1"], index=0, key="terminal_arr")
            
            st.write(t["pax"])
            sub_c1, sub_c2 = st.columns(2)
            with sub_c1:
                adultos = st.number_input(t["adults"], min_value=1, step=1, key="adults_count")
            with sub_c2:
                ninos = st.number_input(t["children"], min_value=0, step=1, key="children_count")

    vuelo_llegada_completo = f"{aerolinea_llegada} {num_vuelo_llegada}".strip()
else:
    col_dep_only_1, col_dep_only_2 = st.columns(2)

    with col_dep_only_1:
        nombre_input = st.text_input(
            t["guest"],
            key="guest_name"
        )
        nombre_huesped = nombre_input.strip().title()

    with col_dep_only_2:
        confirmacion = st.text_input(
            t["conf"],
            key="conf_num"
        ).upper()

    # -------------------------------------
    # PASAJEROS - ONE WAY DEPARTURE
    # -------------------------------------

    st.write(t["pax"])

    col_adultos, col_ninos = st.columns(2)

    with col_adultos:
        adultos = st.number_input(
            t["adults"],
            min_value=1,
            step=1,
            key="adults_count"
        )

    with col_ninos:
        ninos = st.number_input(
            t["children"],
            min_value=0,
            step=1,
            key="children_count"
        )

# --- TAB SALIDA ---
fecha_salida = None
vuelo_salida_completo = ""
hora_salida = datetime.time(15, 0)
hora_pickup = datetime.time(11, 30)

if tipo_viaje in [t["ow_dep"], t["rt"]]:
    with tab2:
        col_dep1, col_dep2, col_dep3 = st.columns(3)
        
        with col_dep1:
            fecha_defecto_salida = (fecha_llegada + datetime.timedelta(days=4)) if tipo_viaje == t["rt"] else st.session_state["date_dep_val"]
            fecha_salida = st.date_input(t["date_dep"], value=fecha_defecto_salida, key="date_dep_val")
            
            if tipo_viaje == t["rt"] and 'seleccion_aerolinea_llegada' in locals():
                # El selector conserva su estado aunque cambie el texto de la aerolínea manual.
                default_idx = lista_aerolineas.index(seleccion_aerolinea_llegada)
                seleccion_aerolinea_salida = st.selectbox(t["airline_dep"], lista_aerolineas, index=default_idx, key=f"air_dep_{seleccion_aerolinea_llegada}")
            else:
                seleccion_aerolinea_salida = st.selectbox(t["airline_dep"], lista_aerolineas, key="air_dep_standalone")

            if seleccion_aerolinea_salida == t["airline_other"]:
                aerolinea_salida = st.text_input(t["airline_custom_dep"], key="air_dep_custom").strip()
            else:
                aerolinea_salida = seleccion_aerolinea_salida

        with col_dep2:
            num_vuelo_salida = st.text_input(t["flight_dep"], key="fl_dep")
            vuelo_salida_completo = f"{aerolinea_salida} {num_vuelo_salida}".strip()
            
            hora_salida_str = st.text_input(t["time_dep"], key="time_dep_val")
            try:
                h_dep, m_dep = map(int, hora_salida_str.split(":"))
                hora_salida = datetime.time(h_dep, m_dep)
            except ValueError:
                st.error("Invalid Departure Time format. Using 15:00 as fallback.")
                hora_salida = datetime.time(15, 0)

        with col_dep3:
            dt_vuelo = datetime.datetime.combine(datetime.date.today(), hora_salida)
            dt_pickup_auto = dt_vuelo - datetime.timedelta(hours=3, minutes=00)
            hora_auto_str = dt_pickup_auto.strftime('%H:%M')
            
            custom_pickup = st.checkbox(t["custom_p"], key="custom_pickup")
            
            if custom_pickup:
                hora_pickup_str = st.text_input(t["p_manual"], value=hora_auto_str, key="pickup_manual")
            else:
                st.text_input(t["p_auto"], value=hora_auto_str, disabled=True)
                hora_pickup_str = hora_auto_str
                
            try:
                h_pick, m_pick = map(int, hora_pickup_str.split(":"))
                hora_pickup = datetime.time(h_pick, m_pick)
            except ValueError:
                hora_pickup = dt_pickup_auto.time()

st.markdown("---")

# --- POLÍTICAS Y REGLAS DINÁMICAS ---
is_dep_only = (tipo_viaje == t["ow_dep"])

if is_dep_only:
    if idioma == "English" or csl_private:
        INFO_POLICIES = (
            "**Hotel Departure Pick-up:** The driver will be waiting for you in the lobby of your hotel.\n"
            "**Waiting Time:** The maximum waiting time is **10 minutes** after your scheduled pick-up time.\n"
            "**No-Show Policy:** After 10 minutes, the service is declared a No-Show and is completely non-refundable.\n"
            "**Modifications:** Contact us at reservations@casadorada.com at least 24 hours before your service.\n"
            "**Have a safe flight back home! We look forward to seeing you soon!**"
        )
    else:
        INFO_POLICIES = (
            "**Salida del Hotel:** El conductor le estará esperando en el lobby de su hotel.\n"
            "**Tiempo de Espera:** El tiempo de espera máximo es de **10 minutos** a partir de su hora programada.\n"
            "**No-Show:** Transcurridos los 10 minutos de tolerancia se considerará No-Show y no se dará reembolso.\n"
            "**Modifications:** Contact us at reservations@casadorada.com al menos 24 horas antes de su servicio.\n"
            "**¡Buen viaje de regreso a casa! ¡Esperamos verle pronto de nuevo!**"
        )
else:
    if idioma == "English" or csl_private:
        INFO_POLICIES = (
            "**Modifications:** Contact us at reservations@casadorada.com at least 24 hours before your service.\n"
            "**Departure Pick-ups:** The driver will wait a maximum of 10 minutes after the scheduled lobby time.\n"
            "**Non-Transferable:** This official service is valid exclusively for the registered guest name.\n"
            "**Toll Free Assistance:** 1-866-448-0151 | Monday to Friday from 8:00 a.m. to 07:00 p.m. (PST)"
        )
    else:
        INFO_POLICIES = (
            "**Modificaciones:** Contáctenos en reservations@casadorada.com al menos 24 horas antes de su servicio.\n"
            "**Recolección de Salida:** El conductor esperará un máximo de 10 minutos después de la hora programada.\n"
            "**No Transferible:** Este servicio oficial es válido exclusivamente para el nombre del huésped registrado.\n"
            "**Asistencia Telefónica Gratuita:** 1-866-448-0151 | Lunes a Viernes de 8:00 a.m. a 07:00 p.m. (PST)"
        )

# --- EXECUTIVE PREMIUM PDF CLASS ---
class VoucherPDF(FPDF):
    def __init__(self, logo_file=None):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.logo_file = logo_file

    def header(self):
        if self.page_no() == 1:
            if self.logo_file:
                try: 
                    self.image(self.logo_file, x=67.5, y=4, w=75, h=0)
                except Exception: 
                    self.placeholder_logo()
            else:
                self.placeholder_logo()

            self.set_xy(12, 54)
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(15, 23, 42)
            self.cell(0, 7, f"Hola, {nombre_huesped}!", ln=1, align="L")
            
            self.set_font("Helvetica", "", 10)
            self.set_text_color(100, 116, 139)
            welcome_text = "We are Corporate Travel Alliance and it will be a pleasure to welcome you." if (idioma == "English" or csl_private) else "Somos Corporate Travel Alliance y será un placer darle la bienvenida."
            self.cell(0, 5, welcome_text, ln=1, align="L")

    def placeholder_logo(self):
        self.set_draw_color(226, 232, 240)
        self.rect(67.5, 4, 75, 20)
        self.set_xy(67.5, 12)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(148, 163, 184)
        self.cell(75, 5, "[ Corporate Travel Alliance ]", align="C")

    def footer(self):
        if self.page_no() == 1:
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(148, 163, 184)
            footer_text = "Corporate Travel Alliance"
            self.cell(0, 10, footer_text, align="C")

    def escribir_linea_mixta(self, x, y, texto_linea, alto_celda, pt_size=9.5, c_normal=(71, 85, 105), c_bold=(15, 23, 42)):
        self.set_xy(x, y)
        segmentos = texto_linea.split("**")
        es_negrita = False
        
        for segmento in segmentos:
            if not segmento:
                es_negrita = not es_negrita
                continue
            if es_negrita:
                self.set_font("Helvetica", "B", pt_size)
                self.set_text_color(*c_bold)
            else:
                self.set_font("Helvetica", "", pt_size)
                self.set_text_color(*c_normal)
            
            ancho_texto = self.get_string_width(segmento)
            self.cell(ancho_texto, alto_celda, segmento, border=0)
            es_negrita = not es_negrita

def crear_pdf(terminal, datos_editables=None):
    pdf = VoucherPDF(logo_file=logo_a_usar)
    if datos_editables is not None:
        pdf.set_keywords(codificar_datos_voucher(datos_editables))
        pdf.set_subject("Corporate Travel Alliance - editable transportation voucher")
    pdf.alias_nb_pages()
    pdf.add_page()
    
    if not is_dep_only:
        # --- BLOQUE 1: PROCEDIMIENTOS DE AEROPUERTO ---
        pdf.set_y(78)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(241, 245, 249)
        pdf.rect(12, 78, 186, 48, style="FD")
        
        pdf.set_xy(16, 81)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(37, 99, 235)
        
        if csl_private:
            proc_title = "AIRPORT PROCEDURES - HOW TO FIND US (CSL PRIVATE AIRPORT)"
            pdf.cell(0, 5, proc_title, ln=1)
            pdf.escribir_linea_mixta(16, 89, "1.  After passing Mexican Immigration, claim luggage and clear Customs.", 5.0)
            pdf.escribir_linea_mixta(16, 97, "2.  Walk outside: Our official staff is **WAITING FOR YOU AT THE PARKING LOT**.", 5.0)
            pdf.escribir_linea_mixta(16, 105, "3.  Look for the recognizable transportation sign shown on the right.", 5.0)
        else:
            proc_title = f"AIRPORT PROCEDURES - HOW TO FIND US ({terminal.upper()})" if idioma == "English" else f"PROCEDIMIENTOS EN EL AEROPUERTO - CÓMO ENCONTRARNOS ({terminal.upper()})"
            pdf.cell(0, 5, proc_title, ln=1)
            
            if terminal == "Terminal 1":
                pdf.set_fill_color(241, 245, 249)
                pdf.rect(16, 88.5, 132, 7, style="F")
                if idioma == "English":
                    pdf.escribir_linea_mixta(16, 89.5, "1.  **PLEASE DO NOT STOP AT THE TIMESHARE BOOTHS.**", 5.0, c_bold=(220, 38, 38))
                    pdf.escribir_linea_mixta(16, 98.0, "2.  **ONCE OUT OUR STAFF WILL BE WAITING FOR YOU IN GROUP EXITS.**", 5.0, c_bold=(15, 23, 42))
                    pdf.escribir_linea_mixta(16, 106.0, "3.  Please take the Groups Exit (first door on your right hand after luggage claim).", 4.5, pt_size=8.5)
                else:
                    pdf.escribir_linea_mixta(16, 89.5, "1.  **POR FAVOR NO SE DETENGA EN LOS MÓDULOS DE TIEMPO COMPARTIDO.**", 5.0, c_bold=(220, 38, 38))
                    pdf.escribir_linea_mixta(16, 98.0, "2.  **UNA VEZ AFUERA NUESTRO PERSONAL LO ESPERARÁ EN LA SALIDA DE GRUPOS.**", 5.0, c_bold=(15, 23, 42))
                    pdf.escribir_linea_mixta(16, 106.0, "3.  Por favor tome la Salida de Grupos (primera puerta a su derecha después del reclamo de equipaje).", 4.5, pt_size=8.5)
            else:
                if idioma == "English":
                    pdf.escribir_linea_mixta(16, 89, "1.  After passing Mexican Immigration, claim luggage and clear Customs.", 5.0)
                    pdf.set_fill_color(241, 245, 249)
                    pdf.rect(16, 95.5, 132, 7, style="F")
                    pdf.escribir_linea_mixta(16, 96.5, "2.  **PLEASE DO NOT STOP AT THE TIMESHARE BOOTHS.**", 5.0, c_bold=(220, 38, 38))
                    pdf.escribir_linea_mixta(16, 104.5, "3.  Walk outside: Our official staff is waiting for you **UNDER UMBRELLA #4**.", 5.0)
                    pdf.escribir_linea_mixta(16, 112.5, "4.  Look for the recognizable transportation sign shown on the right.", 5.0)
                else:
                    pdf.escribir_linea_mixta(16, 89, "1.  Tras pasar la sección de Inmigración, reclame su equipaje y pase Aduanas.", 5.0)
                    pdf.set_fill_color(241, 245, 249)
                    pdf.rect(16, 95.5, 132, 7, style="F")
                    pdf.escribir_linea_mixta(16, 96.5, "2.  **POR FAVOR NO SE DETENGA EN LOS MÓDULOS DE TIEMPO COMPARTIDO.**", 5.0, c_bold=(220, 38, 38))
                    pdf.escribir_linea_mixta(16, 104.5, "3.  Salga del edificio: Nuestro personal oficial le espera **BAJO LA SOMBRILLA #4**.", 5.0)
                    pdf.escribir_linea_mixta(16, 112.5, "4.  Busque el letrero de transporte reconocible que se muestra a la derecha.", 5.0)
            
        if os.path.exists(CARTEL_PATH):
            try: pdf.image(CARTEL_PATH, x=152, y=82, w=35, h=0)
            except Exception: pass

        y_offset_block2 = 132
    else:
        y_offset_block2 = 78

    # --- BLOQUE 2: RESUMEN DE VIAJE ---
    pdf.set_xy(12, y_offset_block2)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(226, 232, 240)
    
    rect_height = 26
    if requiere_car_seats and requiere_grocery:
        rect_height = 32
    pdf.rect(12, y_offset_block2, 186, rect_height, style="FD")
    
    pdf.set_xy(15, y_offset_block2 + 3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, "TRIP SUMMARY" if (idioma == "English" or csl_private) else "RESUMEN DEL VIAJE", ln=1)
    
    pdf.set_xy(15, y_offset_block2 + 11)
    
    # 1. Confirmación
    label_conf = "Confirmation Number: " if (idioma == "English" or csl_private) else "No. de Confirmación: "
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(pdf.get_string_width(label_conf), 5, label_conf)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(pdf.get_string_width(confirmacion) + 8, 5, confirmacion)
    
    # 2. Tipo de Transfer
    label_type = "Transfer Type: " if (idioma == "English" or csl_private) else "Tipo de Traslado: "
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(pdf.get_string_width(label_type), 5, label_type)
    
    if tipo_viaje == t["rt"]:
        tt_val = "Round Trip" if (idioma == "English" or csl_private) else "Viaje Redondo"
    elif tipo_viaje == t["ow_dep"]:
        tt_val = "One Way (Departure)" if (idioma == "English" or csl_private) else "Sencillo (Salida)"
    else:
        tt_val = "One Way" if (idioma == "English" or csl_private) else "Viaje Sencillo"
        
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(pdf.get_string_width(tt_val) + 8, 5, tt_val)
    
    # 3. Pasajeros
    label_pax = "Passengers: " if (idioma == "English" or csl_private) else "Pasajeros: "
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(pdf.get_string_width(label_pax), 5, label_pax)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(15, 23, 42)
    pax_txt = f"{adultos} Ad. / {ninos} Ch." if (idioma == "English" or csl_private) else f"{adultos} Ad. / {ninos} Niñ."
    pdf.cell(0, 5, pax_txt, ln=1)
    
    if (requiere_car_seats or requiere_grocery) and not is_dep_only:
        pdf.set_xy(15, y_offset_block2 + 18)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(38, 5, "Special Add-on:" if (idioma == "English" or csl_private) else "Servicios Adicionales:")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(37, 99, 235)
        
        addons_list = []
        if requiere_car_seats:
            addons_list.append("Complimentary Car Seat" if (idioma == "English" or csl_private) else "Asiento de Bebé")
        if requiere_grocery:
            addons_list.append("Grocery Stop" if (idioma == "English" or csl_private) else "Parada de Súper")
            
        pdf.cell(0, 5, " | ".join(addons_list))

    # --- BLOQUE 3: DETALLES ---
    y_offset_block3 = y_offset_block2 + rect_height + 6
    meses_es = {"January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril", "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto", "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"}

    if is_dep_only:
        # Bloque de salida ancho completo
        pdf.set_xy(12, y_offset_block3)
        pdf.rect(12, y_offset_block3, 186, 42, style="FD")
        
        pdf.set_xy(15, y_offset_block3 + 3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 5, "DEPARTURE DETAILS" if (idioma == "English" or csl_private) else "DETALLES DE SALIDA", ln=1)
        
        fecha_salida_str_pdf = fecha_salida.strftime('%B %d, %Y')
        if idioma != "English" and not csl_private:
            for eng, esp in meses_es.items():
                fecha_salida_str_pdf = fecha_salida_str_pdf.replace(eng, esp)

        datos_dep = [
            ("Departure Date:" if (idioma == "English" or csl_private) else "Fecha de Salida:", fecha_salida_str_pdf),
            ("Flight & Airline:" if (idioma == "English" or csl_private) else "Vuelo y Aerolínea:", vuelo_salida_completo),
            ("Flight Time:" if (idioma == "English" or csl_private) else "Hora del Vuelo:", hora_salida.strftime('%I:%M %p')),
            ("Hotel Pick-up:" if (idioma == "English" or csl_private) else "Pick-up en Hotel:", f"{hora_pickup.strftime('%I:%M %p')} (Lobby)")
        ]
        y_item = y_offset_block3 + 11
        for label, val in datos_dep:
            pdf.set_xy(15, y_item)
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(45, 5, label)
            if "Pick-up" in label:
                pdf.set_font("Helvetica", "B", 10.5)
                pdf.set_text_color(37, 99, 235)
            else:
                pdf.set_font("Helvetica", "", 10.5)
                pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 5, str(val))
            y_item += 6.5
            
    else:
        # Columnas Izquierda y Derecha convencionales
        pdf.set_xy(12, y_offset_block3)
        pdf.rect(12, y_offset_block3, 91, 42, style="FD")
        
        pdf.set_xy(15, y_offset_block3 + 3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 5, "ARRIVING DETAILS" if (idioma == "English" or csl_private) else "DETALLES DE LLEGADA", ln=1)
        
        fecha_llegada_str_pdf = fecha_llegada.strftime('%B %d, %Y')
        if idioma != "English" and not csl_private:
            for eng, esp in meses_es.items():
                fecha_llegada_str_pdf = fecha_llegada_str_pdf.replace(eng, esp)

        datos_arr = [
            ("Arrival Date:" if (idioma == "English" or csl_private) else "Fecha de Llegada:", fecha_llegada_str_pdf),
            ("Flight & Airline:" if (idioma == "English" or csl_private) else "Vuelo y Aerolínea:", vuelo_llegada_completo),
            ("Arrival Time:" if (idioma == "English" or csl_private) else "Hora de Llegada:", hora_llegada.strftime('%I:%M %p')),
            ("Location / Terminal:" if (idioma == "English" or csl_private) else "Lugar / Terminal:", terminal)
        ]
        y_item = y_offset_block3 + 11
        for label, val in datos_arr:
            pdf.set_xy(15, y_item)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(34, 5, label)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 5, str(val))
            y_item += 5.5

        # Columna Derecha
        pdf.set_xy(107, y_offset_block3)
        pdf.rect(107, y_offset_block3, 91, 42, style="FD")
        
        pdf.set_xy(110, y_offset_block3 + 3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 5, "RETURNING DETAILS" if (idioma == "English" or csl_private) else "DETALLES DE REGRESO", ln=1)
        
        if tipo_viaje == t["rt"]:
            fecha_salida_str_pdf = fecha_salida.strftime('%B %d, %Y')
            if idioma != "English" and not csl_private:
                for eng, esp in meses_es.items():
                    fecha_salida_str_pdf = fecha_salida_str_pdf.replace(eng, esp)

            datos_dep = [
                ("Departure Date:" if (idioma == "English" or csl_private) else "Fecha de Salida:", fecha_salida_str_pdf),
                ("Flight & Airline:" if (idioma == "English" or csl_private) else "Vuelo y Aerolínea:", vuelo_salida_completo),
                ("Flight Time:" if (idioma == "English" or csl_private) else "Hora del Vuelo:", hora_salida.strftime('%I:%M %p')),
                ("Hotel Pick-up:" if (idioma == "English" or csl_private) else "Pick-up en Hotel:", f"{hora_pickup.strftime('%I:%M %p')} (Lobby)")
            ]
            y_item = y_offset_block3 + 11
            for label, val in datos_dep:
                pdf.set_xy(110, y_item)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(100, 116, 139)
                pdf.cell(32, 5, label)
                if "Pick-up" in label:
                    pdf.set_font("Helvetica", "B", 9.5)
                    pdf.set_text_color(37, 99, 235)
                else:
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(15, 23, 42)
                pdf.cell(0, 5, str(val))
                y_item += 5.5
        else:
            pdf.set_xy(110, y_offset_block3 + 18)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(148, 163, 184)
            no_ret_txt = "No return service requested for this trip." if (idioma == "English" or csl_private) else "No se solicitó servicio de regreso."
            pdf.cell(0, 5, no_ret_txt)

    # --- BLOQUE 4: NOTAS DE VIAJE ---
    y_offset_block4 = y_offset_block3 + 48
    pdf.set_xy(12, y_offset_block4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, "IMPORTANT TRAVELER NOTES" if (idioma == "English" or csl_private) else "NOTAS IMPORTANTES PARA EL VIAJERO", ln=1)
    
    y_policy = y_offset_block4 + 7
    for linea in INFO_POLICIES.split("\n"):
        pdf.escribir_linea_mixta(12, y_policy, linea, 4.5, pt_size=9, c_normal=(30, 41, 59), c_bold=(15, 23, 42))
        y_policy += 5.5
    
    # --- PÁGINA 2: MAPA (Solo si NO es salida exclusiva Y NO es aeropuerto privado CSL) ---
    if not is_dep_only and not csl_private:
        pdf.add_page()
        mapa_a_usar = "map1.png" if terminal == "Terminal 1" else "Map.png"
        
        if os.path.exists(mapa_a_usar):
            pdf.set_auto_page_break(False, margin=0)
            pdf.image(mapa_a_usar, x=0, y=0, w=210, h=297)
            pdf.set_auto_page_break(True, margin=10)
        else:
            pdf.set_text_color(239, 68, 68)
            pdf.set_font("Helvetica", "B", 12)
            err_map_txt = f"[Error: '{mapa_a_usar}' is missing]" if idioma == "English" else f"[Error: Falta el archivo '{mapa_a_usar}']"
            pdf.cell(0, 20, err_map_txt, ln=1, align="C")

    return pdf.output(dest='S')

def datos_actuales_voucher():
    """Valores originales del formulario, para permitir recuperar y editar nuevos PDFs."""
    return {
        "schema_version": 1,
        "type": tipo_viaje_code,
        "language": idioma,
        "guest_name": nombre_huesped,
        "confirmation": confirmacion,
        "arrival_date": fecha_llegada.isoformat() if tipo_viaje_code != "departure" else "",
        "departure_date": fecha_salida.isoformat() if fecha_salida else "",
        "arrival_airline": aerolinea_llegada if tipo_viaje_code != "departure" else "",
        "arrival_flight": num_vuelo_llegada if tipo_viaje_code != "departure" else "",
        "arrival_time": hora_llegada.strftime("%H:%M"),
        "departure_airline": aerolinea_salida if tipo_viaje_code != "arrival" else "",
        "departure_flight": num_vuelo_salida if tipo_viaje_code != "arrival" else "",
        "departure_time": hora_salida.strftime("%H:%M"),
        "pickup_time": hora_pickup.strftime("%H:%M"),
        "manual_pickup": bool(custom_pickup),
        "terminal": terminal_seleccionada if tipo_viaje_code != "departure" else "",
        "csl_private": bool(csl_private),
        "adults": int(adultos),
        "children": int(ninos),
        "car_seats": bool(requiere_car_seats),
        "grocery": bool(requiere_grocery),
    }

# --- BUTTON ACTION PROCESSING ---
st.markdown(t["btn_process"])

if st.button(
    ("💾 Regenerate corrected PDF" if idioma == "English" else "💾 Generar voucher corregido")
    if modo_voucher == "modificar" else t["btn_gen"],
    type="primary", use_container_width=True,
):
    if not nombre_input.strip():
        st.error(t["err_name"])
    elif not confirmacion.strip():
        st.error(t["err_req"])
    elif tipo_viaje in [t["ow_arr"], t["rt"]] and not aerolinea_llegada:
        st.error(t["err_airline"])
    elif tipo_viaje in [t["ow_dep"], t["rt"]] and not aerolinea_salida:
        st.error(t["err_airline"])
    elif tipo_viaje == t["rt"] and not num_vuelo_salida:
        st.error(t["err_dep"])
    else:
        try:
            datos_para_pdf = datos_actuales_voucher()
            pdf_raw = crear_pdf(terminal_seleccionada, datos_para_pdf)
            # fpdf2 devuelve bytearray; PyFPDF antiguo devuelve str.
            pdf_data = pdf_raw.encode("latin-1") if isinstance(pdf_raw, str) else bytes(pdf_raw)

            if tipo_viaje == t["rt"]:
                tag_viaje = "Roundtrip"
            elif tipo_viaje == t["ow_dep"]:
                tag_viaje = "Departure"
            else:
                tag_viaje = "One Way"

            nombre_archivo_pdf = f"{tag_viaje} Transportation voucher- {confirmacion}- {nombre_huesped}.pdf"
            st.session_state["pdf_generado"] = pdf_data
            st.session_state["pdf_generado_datos"] = datos_para_pdf
            st.session_state["pdf_generado_nombre"] = nombre_archivo_pdf
            st.success(t["success"])
        except Exception as e:
            st.error(
                f"Technical error during PDF compilation: {e}"
                if idioma == "English"
                else f"Error técnico durante la compilación del PDF: {e}"
            )

# La vista previa y la descarga permanecen al interactuar con la página.
if st.session_state.get("pdf_generado") is not None:
    if st.session_state.get("pdf_generado_datos") != datos_actuales_voucher():
        st.info("Form details have changed. Generate the PDF again to apply them."
                if idioma == "English"
                else "Modificaste los datos. Vuelve a generar el PDF para aplicar los cambios.")
    else:
        # -------------------------------------
        # VISTA PREVIA DEL VOUCHER PDF
        # -------------------------------------
        st.subheader("PDF Preview" if idioma == "English" else "Vista previa del PDF")
        st.pdf(st.session_state["pdf_generado"], height=700)

        # -------------------------------------
        # DESCARGAR VOUCHER
        # -------------------------------------
        st.download_button(
            label=t["btn_dl"],
            data=st.session_state["pdf_generado"],
            file_name=st.session_state["pdf_generado_nombre"],
            mime="application/pdf",
            use_container_width=True,
        )
        st.info(
            "Para limpiar el formulario para un nuevo cliente, haz clic en el botón 'Limpiar Formulario' en la barra izquierda."
            if idioma != "English"
            else "To clear the form for a new client, click 'Reset Form' on the left sidebar."
        )
