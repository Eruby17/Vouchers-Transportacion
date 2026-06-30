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

# --- TEXTOS OFICIALES EN INGLÉS ---
INFO_ARRIVALS = (
    "AIRPORT PROCEDURES FOR YOUR ARRIVAL: "
    "After passing Mexican Immigration, claim checked luggage and clear Customs, "
    "PLEASE DON'T STOP WITH TIMESHARED BOOTH, THEY WILL TRY TO SELL TRANSPORTATION and "
    "REMEMBER OUR STAFF WILL BE HOLDING A SIGN WITH THE TRANSPORTATION COMPANY LOGO. "
    "ONCE OUT OUR STAFF IS UNDER UMBRELLA # 4 WHERE WILL BE WAITING FOR YOU."
)

INFO_POLICIES = (
    "- For any modifications, you must contact us directly at reservations@casadorada.com and "
    "reservationscd@casadorada.com. Any modifications require to be asked for and confirmed "
    "at least 24 hours before the service.\n"
    "- Please be aware that for departures, the driver will wait up to 10 additional minutes "
    "from the scheduled pick-up time. After this time, the driver will have to leave the "
    "hotel, and the company will not be able to provide a refund.\n"
    "- Please be advised that the transportation service is arranged by the name of guest reservation. "
    "This service is not transferable and cannot be changed to another guest as a gift.\n"
    "Reservations Toll Free: 1-866-448-0151 | Monday to Friday from 8:00 a.m. to 07:00 p.m. (Pacific Time)"
)

# --- CLASE PDF ---
class VoucherPDF(FPDF):
    def __init__(self, logo_file=None):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.logo_file = logo_file

    def header(self):
        # Condición: Solo renderizar header si estamos en la Página 1
        if self.page_no() == 1:
            if self.logo_file:
                self.image(self.logo_file, 12, 10, 45)
            
            self.set_font("Helvetica", "B", 15)
            self.set_text_color(26, 54, 93) # Azul Marino Corporativo
            self.cell(0, 12, "OFFICIAL TRANSPORTATION VOUCHER", ln=1, align="R")
            self.ln(10)

    def footer(self):
        # Condición: Solo renderizar footer si estamos en la Página 1
        if self.page_no() == 1:
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 10, "Page 1/2 - Casa Dorada Resort and Spa", align="C")

def crear_pdf():
    pdf = VoucherPDF(logo_file=logo_subido)
    pdf.alias_nb_pages()
    
    # --- PÁGINA 1: DATOS, ARRIBOS Y POLÍTICAS ---
    pdf.add_page()
    
    # Bloque de Título de la sección
    pdf.set_fill_color(26, 54, 93)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "  RESERVATION DETAILS", ln=1, fill=True)
    pdf.ln(2)
    
    def write_row_table(label, val):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(50, 6, label, border="B")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, val, ln=1, border="B")

    write_row_table("Guest Name:", nombre_huesped)
    write_row_table("Service Type:", "Round Trip" if tipo_viaje == "Round Trip" else "One Way (Arrival Only)")
    write_row_table("Confirmation Number:", confirmacion)
    write_row_table("Passengers:", f"{adultos} Adults / {ninos} Children")
    if requiere_car_seats:
        write_row_table("Special Request:", "Car Seat Included")
        
    pdf.ln(5)
    
    # Sección de Llegada
    pdf.set_fill_color(26, 54, 93)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "  ARRIVAL FLIGHT DETAILS", ln=1, fill=True)
    pdf.ln(2)
    
    write_row_table("Arrival Date:", fecha_llegada.strftime('%B %d, %Y'))
    write_row_table("Arrival Flight:", vuelo_llegada_completo)
    write_row_table("Estimated Time of Arrival:", f"{hora_llegada.strftime('%H:%M')} HRS")
    
    pdf.ln(5)
    
    # Sección de Salida si aplica
    if tipo_viaje == "Round Trip":
        pdf.set_fill_color(26, 54, 93)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "  DEPARTURE FLIGHT DETAILS", ln=1, fill=True)
        pdf.ln(2)
        
        write_row_table("Departure Date:", fecha_salida.strftime('%B %d, %Y'))
        write_row_table("Departure Flight:", vuelo_salida_completo)
        write_row_table("Flight Departure Time:", f"{hora_salida.strftime('%H:%M')} HRS")
        write_row_table("Scheduled Pick-up Time:", f"{hora_pickup.strftime('%H:%M')} HRS (From Hotel)")
        pdf.ln(5)
    
    # Recuadro de Alerta de Llegada en Aeropuerto
    pdf.set_fill_color(255, 243, 205) # Color de alerta suave (amarillo/crema)
    pdf.set_text_color(133, 100, 4)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.multi_cell(0, 5, INFO_ARRIVALS, border=1, align="L", fill=True)
    
    pdf.ln(5)
    
    # Sección de Políticas Integrada Abajo de forma limpia
    pdf.set_fill_color(240, 244, 248) # Gris azulado muy tenue para el fondo
    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "  IMPORTANT POLICIES & TERMS", ln=1, fill=True)
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.multi_cell(0, 4.2, INFO_POLICIES, border=0, align="L", fill=True)
    
    # --- PÁGINA 2: MAPA A SANGRE (FULL PAGE) ---
    pdf.add_page()
    
    if os.path.exists(MAPA_PATH):
        # Desactivamos temporalmente el salto automático de página y márgenes para el full-bleed
        pdf.set_auto_page_break(False, margin=0)
        # Forzamos que la imagen cubra exactamente las dimensiones A4 (210 x 297 mm) sin dejar bordes
        pdf.image(MAPA_PATH, x=0, y=0, w=210, h=297)
        # Reactivamos por si acaso se agregan más hojas a futuro
        pdf.set_auto_page_break(True, margin=10)
    else:
        pdf.set_text_color(200, 0, 0)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 20, f"[Error: '{MAPA_PATH}' no encontrado para la vista completa]", ln=1, align="C")

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
