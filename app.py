import streamlit as st
import datetime
from fpdf import FPDF
import os

# Configuración de la página en Streamlit
st.set_page_config(page_title="Generador de Vouchers Casa Dorada", layout="wide", page_icon="📋")

st.title("📋 Creador de Vouchers de Transportación — Casa Dorada")
st.write("Completa los datos del servicio para generar el archivo PDF de dos páginas.")

# --- ARCHIVOS ESTÁTICOS ---
MAPA_PATH = "Map.png"

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración del Logo")
logo_subido = st.sidebar.file_uploader("Subir Logo de la Empresa (PNG o JPG)", type=["png", "jpg", "jpeg"])

if logo_subido:
    st.sidebar.success("✅ Logo cargado para este voucher.")
else:
    st.sidebar.info("ℹ️ El voucher se generará con el espacio de logo en blanco si no subes uno.")

st.sidebar.markdown("---")
if os.path.exists(MAPA_PATH):
    st.sidebar.success("✅ 'Map.png' detectado para la Página 2.")
else:
    st.sidebar.warning("⚠️ No se encontró 'Map.png' en la raíz de GitHub.")

# --- FORMULARIO PRINCIPAL ---
st.subheader("Datos del Servicio")

# Selección de Tipo de Viaje
tipo_viaje = st.radio("Tipo de Servicio / Service Type", ["One Way (Arrival Only)", "Round Trip"], horizontal=True)

st.markdown("### 🛬 Arrival Information")
col1, col2, col3 = st.columns(3)

# Aerolíneas solicitadas
lista_aerolineas = [
    "Alaska Airlines", 
    "American Airlines", 
    "Southwest Airlines", 
    "Delta Airlines", 
    "Aeroméxico", 
    "WestJet Airlines"
]

with col1:
    nombre_input = st.text_input("Guest Name (Puedes pegar en MAYÚSCULAS)", placeholder="Ej: ALFREDO RIVERA")
    nombre_huesped = nombre_input.strip().title()
    fecha_llegada = st.date_input("Arrival Date", datetime.date.today())

with col2:
    aerolinea_llegada = st.selectbox("Arrival Airline", lista_aerolineas, key="air_arr")
    num_vuelo_llegada = st.text_input("Arrival Flight Number", placeholder="Ej: 2468", key="num_arr")
    hora_llegada = st.time_input("Estimated Time of Arrival (ETA)", datetime.time(12, 0), step=60)

with col3:
    confirmacion = st.text_input("Confirmation Number", placeholder="Ej: CD-98765").upper()
    adultos = st.number_input("Adultos / Adults", min_value=1, value=2, step=1)
    ninos = st.number_input("Niños / Children", min_value=0, value=0, step=1)
    requiere_car_seats = st.checkbox("¿Requiere Car Seats?")

vuelo_llegada_completo = f"{aerolinea_llegada} {num_vuelo_llegada}".strip()

# --- SECCIÓN DINÁMICA DE SALIDA (ROUND TRIP) ---
fecha_salida = None
vuelo_salida_completo = ""
hora_salida = None
hora_pickup = None

if tipo_viaje == "Round Trip":
    st.markdown("---")
    st.markdown("### 🛫 Departure Information")
    col_dep1, col_dep2, col_dep3 = st.columns(3)
    
    with col_dep1:
        fecha_salida = st.date_input("Departure Date", datetime.date.today() + datetime.timedelta(days=5))
        aerolinea_salida = st.selectbox("Departure Airline", lista_aerolineas, key="air_dep")

    with col_dep2:
        num_vuelo_salida = st.text_input("Departure Flight Number", placeholder="Ej: 1357", key="num_dep")
        vuelo_salida_completo = f"{aerolinea_salida} {num_vuelo_salida}".strip()
        hora_salida = st.time_input("Flight Departure Time", datetime.time(15, 0), step=60)

    with col_dep3:
        dt_vuelo = datetime.datetime.combine(datetime.date.today(), hora_salida)
        dt_pickup_default = dt_vuelo - datetime.timedelta(hours=3, minutes=30)
        hora_pickup = st.time_input("Scheduled Pick-up Time (Auto-calculated)", dt_pickup_default.time(), step=60)

st.markdown("---")

# --- TEXTOS OFICIALES RECONFIGURADOS (MÁS AMIGABLES) ---
INFO_ARRIVALS = (
    "After passing Mexican Immigration, claim checked luggage and clear Customs. "
    "PLEASE DO NOT STOP AT THE TIMESHARE BOOTHS (they will try to sell you unauthorized transportation). "
    "Our official staff will be waiting for you outside under UMBRELLA #4, holding the company sign."
)

INFO_POLICIES = (
    "- For any modifications, contact us at reservations@casadorada.com at least 24 hours in advance.\n"
    "- For departures, the driver will wait a maximum of 10 minutes from the scheduled pick-up time.\n"
    "- This service is personal, non-transferable, and valid only for the registered guest name.\n"
    "Reservations Toll Free: 1-866-448-0151 | Mon-Fri 8:00 a.m. to 07:00 p.m. (Pacific Time)"
)

# --- CLASE PDF ---
class VoucherPDF(FPDF):
    def __init__(self, logo_file=None):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.logo_file = logo_file

    def header(self):
        if self.page_no() == 1:
            # Espacio para el Logo de la Compañía (Izquierda)
            if self.logo_file:
                self.image(self.logo_file, 12, 12, 45)
            else:
                # Recuadro guía si no se sube logo
                self.set_draw_color(200, 200, 200)
                self.rect(12, 12, 45, 15)
                self.set_xy(12, 17)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(150, 150, 150)
                self.cell(45, 5, "[ Espacio para Logo ]", align="C")

            # Saludo Amistoso y Personalizado (Derecha)
            self.set_xy(100, 14)
            self.set_font("Helvetica", "B", 16)
            self.set_text_color(26, 54, 93) # Azul corporativo elegante
            self.cell(0, 8, f"¡Hola, {nombre_huesped}!", ln=1, align="R")
            self.ln(12)

    def footer(self):
        if self.page_no() == 1:
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(140, 140, 140)
            self.cell(0, 10, "Casa Dorada Resort and Spa — Página 1/2", align="C")

def crear_pdf():
    pdf = VoucherPDF(logo_file=logo_subido)
    pdf.alias_nb_pages()
    
    # --- PÁGINA 1: FORMATO FACTURA / INVOICE ---
    pdf.add_page()
    
    # --- BLOQUE CENTRAL: AIRPORT PROCEDURES & SIGN SPACE ---
    pdf.set_fill_color(245, 247, 250)
    pdf.set_draw_color(218, 226, 236)
    pdf.rect(12, pdf.get_y(), 186, 38, fill=True)
    
    pdf.set_xy(16, pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 5, "AIRPORT PROCEDURES FOR YOUR ARRIVAL", ln=1)
    
    pdf.set_x(16)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 72, 88)
    pdf.multi_cell(115, 4.5, INFO_ARRIVALS, border=0, align="L")
    
    # Cuadro interno para el SIGN de la compañía dentro del bloque
    pdf.set_xy(140, pdf.get_y() - 25)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(180, 190, 210)
    pdf.rect(140, pdf.get_y(), 50, 22, fill=True)
    pdf.set_y(pdf.get_y() + 6)
    pdf.set_x(140)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 110, 130)
    pdf.cell(50, 4, "RECOGNIZABLE SIGN / LOGO", ln=1, align="C")
    pdf.set_x(140)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.cell(50, 4, "[ Espacio del Letrero ]", ln=1, align="C")
    
    pdf.set_y(74) # Ajuste de flujo hacia abajo
    
    # --- FUNCIÓN REUTILIZABLE PARA TABLAS ESTILO FACTURA ---
    def item_factura(label, valor, alternar_fondo):
        if alternar_fondo:
            pdf.set_fill_color(248, 250, 252) # Efecto cebra muy tenue
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.set_draw_color(230, 235, 242)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(70, 80, 95)
        pdf.cell(65, 7.5, f"  {label}", border="B", fill=True)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 7.5, str(valor), border="B", ln=1, fill=True)

    # --- TABLA 1: DATOS DE CONFIRMACIÓN ---
    pdf.set_fill_color(26, 54, 93)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "  SERVICE SUMMARY / DATOS DEL SERVICIO", ln=1, fill=True)
    
    item_factura("Confirmation Number:", confirmacion, False)
    item_factura("Service Type / Tipo de Viaje:", "Round Trip" if tipo_viaje == "Round Trip" else "One Way (Arrival Only)", True)
    item_factura("Passengers / Pasajeros:", f"{adultos} Adults / {ninos} Children", False)
    if requiere_car_seats:
        item_factura("Special Requests:", "Car Seat Included", True)
        
    pdf.ln(4)
    
    # --- TABLA 2: DETALLES DE LLEGADA ---
    pdf.set_fill_color(26, 54, 93)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "  ARRIVAL DETAILS / INFORMACIÓN DE LLEGADA", ln=1, fill=True)
    
    item_factura("Arrival Date:", fecha_llegada.strftime('%B %d, %Y'), False)
    item_factura("Flight & Airline:", vuelo_llegada_completo, True)
    item_factura("Estimated Arrival Time (ETA):", f"{hora_llegada.strftime('%H:%M')} HRS", False)
    
    pdf.ln(4)
    
    # --- TABLA 3: DETALLES DE SALIDA (SI APLICA) ---
    if tipo_viaje == "Round Trip":
        pdf.set_fill_color(26, 54, 93)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "  DEPARTURE DETAILS / INFORMACIÓN DE SALIDA", ln=1, fill=True)
        
        item_factura("Departure Date:", fecha_salida.strftime('%B %d, %Y'), False)
        item_factura("Flight & Airline:", vuelo_salida_completo, True)
        item_factura("Flight Departure Time:", f"{hora_salida.strftime('%H:%M')} HRS", False)
        item_factura("Scheduled Pick-up Time:", f"{hora_pickup.strftime('%H:%M')} HRS (From Hotel Lobby)", True)
        pdf.ln(4)
    
    # --- POLÍTICAS Y TÉRMINOS EN LA BASE ---
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(200, 210, 220)
    pdf.set_text_color(51, 65, 85)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6.5, "  TERMS & IMPORTANT POLICIES", ln=1, fill=True, border="T")
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(0, 4, INFO_POLICIES, border=0, align="L")
    
    # --- PÁGINA 2: MAPA A SANGRE (FULL PAGE SIN BORDES NI TEXTO) ---
    pdf.add_page()
    
    if os.path.exists(MAPA_PATH):
        pdf.set_auto_page_break(False, margin=0)
        pdf.image(MAPA_PATH, x=0, y=0, w=210, h=297)
        pdf.set_auto_page_break(True, margin=10)
    else:
        pdf.set_text_color(200, 0, 0)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 20, f"[Error: Archivo '{MAPA_PATH}' requerido para pantalla completa no disponible]", ln=1, align="C")

    return pdf.output()

# --- ACCIÓN DEL BOTÓN ---
if st.button("🚀 Generar Voucher PDF", type="primary"):
    if not nombre_input:
        st.error("Por favor ingresa el nombre del huésped.")
    elif not confirmacion or not num_vuelo_llegada:
        st.error("Por favor completa los campos obligatorios (Confirmation Number y Flight Number) antes de continuar.")
    elif tipo_viaje == "Round Trip" and not num_vuelo_salida:
        st.error("Por favor ingresa el número de vuelo de salida para el servicio Round Trip.")
    else:
        try:
            pdf_data = bytes(crear_pdf())
            st.success("¡Voucher generado con éxito!")
            
            st.download_button(
                label="📥 Descargar Voucher (PDF)",
                data=pdf_data,
                file_name=f"Voucher_{confirmacion}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error técnico al compilar el PDF: {e}")
