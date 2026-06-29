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
    # Se convierte a formato de Nombre Propio Limpio (Primera letra Mayúscula, resto minúsculas)
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

# Concatenación para el voucher (ej: American Airlines 2468)
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
        # Cálculo por default: 3 horas y media antes del vuelo de salida
        dt_vuelo = datetime.datetime.combine(datetime.date.today(), hora_salida)
        dt_pickup_default = dt_vuelo - datetime.timedelta(hours=3, minutes=30)
        
        hora_pickup = st.time_input("Scheduled Pick-up Time (Auto-calculated)", dt_pickup_default.time(), step=60)

st.markdown("---")

# --- TEXTOS OFICIALES EN INGLÉS ---
INFO_ARRIVALS = (
    "AIRPORT PROCEDURES FOR YOUR ARRIVAL:\n"
    "After passing Mexican Immigration, claim checked luggage and clear Customs, "
    "PLEASE DON'T STOP WITH TIMESHARED BOOTH, THEY WILL TRY TO SELL TRANSPORTATION and "
    "REMEMBER OUR STAFF WILL BE HOLDING A SIGN WITH THE TRANSPORTATION COMPANY LOGO. "
    "ONCE OUT OUR STAFF IS UNDER UMBRELLA # 4 WHERE WILL BE WAITING FOR YOU."
)

INFO_POLICIES = (
    "IMPORTANT POLICIES AND CONTACT INFO:\n\n"
    "- For any modifications, you must contact us directly at reservations@casadorada.com and "
    "reservationscd@casadorada.com. Any modifications require to be asked for and confirmed "
    "at least 24 hours before the service.\n\n"
    "- Please be aware that for departures, the driver will wait up to 10 additional minutes "
    "from the scheduled pick-up time. After this time, the driver will have to leave the "
    "hotel, and the company will not be able to provide a refund.\n\n"
    "- Please be advised that the transportation service is arranged by the name of guest reservation. "
    "This service is not transferable and cannot be changed to another guest as a gift.\n\n"
    "Reservations Toll Free: 1-866-448-0151\n"
    "Monday to Friday from 8:00 a.m. to 07:00 p.m. (Pacific Time)"
)

# --- CLASE PDF ---
class VoucherPDF(FPDF):
    def __init__(self, logo_file=None):
        super().__init__()
        self.logo_file = logo_file

    def header(self):
        if self.logo_file:
            self.image(self.logo_file, 10, 8, 45)
        
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, "OFFICIAL TRANSPORTATION VOUCHER", ln=1, align="R")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} - Casa Dorada Resort and Spa", align="C")

def crear_pdf():
    pdf = VoucherPDF(logo_file=logo_subido)
    pdf.alias_nb_pages()
    
    # --- PÁGINA 1: DATOS DE RESERVA ---
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "RESERVATION DETAILS", ln=1)
    pdf.line(10, 38, 200, 38)
    pdf.ln(3)
    
    def write_row(label, val):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(60, 8, label)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, val, ln=1)

    write_row("Guest Name:", nombre_huesped)
    write_row("Service Type:", "Round Trip" if tipo_viaje == "Round Trip" else "One Way (Arrival Only)")
    write_row("Confirmation Number:", confirmacion)
    write_row("Passengers:", f"{adultos} Adults / {ninos} Children")
    
    if requiere_car_seats:
        write_row("Special Request:", "Car Seat")
        
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "ARRIVAL FLIGHT DETAILS", ln=1)
    pdf.line(10, pdf.get_y(), 100, pdf.get_y())
    pdf.ln(2)
    
    write_row("Arrival Date:", fecha_llegada.strftime('%B %d, %Y'))
    write_row("Arrival Flight:", vuelo_llegada_completo)
    write_row("Estimated Time of Arrival:", f"{hora_llegada.strftime('%H:%M')} HRS")
    
    if tipo_viaje == "Round Trip":
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "DEPARTURE FLIGHT DETAILS", ln=1)
        pdf.line(10, pdf.get_y(), 100, pdf.get_y())
        pdf.ln(2)
        
        write_row("Departure Date:", fecha_salida.strftime('%B %d, %Y'))
        write_row("Departure Flight:", vuelo_salida_completo)
        write_row("Flight Departure Time:", f"{hora_salida.strftime('%H:%M')} HRS")
        write_row("Scheduled Pick-up Time:", f"{hora_pickup.strftime('%H:%M')} HRS (From Hotel)")
    
    pdf.ln(10)
    
    # Recuadro de Alerta
    pdf.set_fill_color(255, 242, 204)
    pdf.set_text_color(150, 80, 0)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.multi_cell(0, 6, INFO_ARRIVALS, border=1, align="L", fill=True)
    
    # --- PÁGINA 2: MAPA Y POLÍTICAS ---
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "WHERE TO FIND US (AIRPORT MAP)", ln=1, align="C")
    pdf.ln(2)
    
    if os.path.exists(MAPA_PATH):
        pdf.image(MAPA_PATH, x=25, y=32, w=160)
        pdf.ln(95)
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 10, f"[Airport Map '{MAPA_PATH}' not found in repository]", ln=1, align="C")
        pdf.ln(15)
        
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, INFO_POLICIES, border=0, align="L")

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
            # La conversión explícita a bytes() garantiza la descarga directa en navegadores sin fallas de formato binario
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
