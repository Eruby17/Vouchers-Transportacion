import streamlit as st
import datetime
from fpdf import FPDF
import os

# Configuración de la página en Streamlit
st.set_page_config(page_title="Generador de Vouchers Corporate Travel Alliance", layout="wide", page_icon="📋")

st.title("📋 Creador de Vouchers de Transportación - Corporate Travel Alliance")
st.write("Completa los datos del servicio para generar el archivo PDF de dos páginas.")

# --- ARCHIVOS ESTÁTICOS ---
MAPA_PATH = "Map.png"
LOGO_DEFAULT_PATH = "logo.jpeg"
CARTEL_PATH = "cartel.png"

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración del Logo")
logo_subido = st.sidebar.file_uploader("Subir Logo de la Empresa (PNG o JPG)", type=["png", "jpg", "jpeg"])

# Determinar qué logo usar
logo_a_usar = None
if logo_subido:
    logo_a_usar = logo_subido
    st.sidebar.success("✅ Usando el logo cargado desde el buscador.")
elif os.path.exists(LOGO_DEFAULT_PATH):
    logo_a_usar = LOGO_DEFAULT_PATH
    st.sidebar.success("✅ 'logo.jpeg' detectado automáticamente en el repositorio.")
else:
    st.sidebar.info("ℹ️ El voucher se generará con el espacio de logo en blanco si no subes uno o agregas 'logo.jpeg'.")

st.sidebar.markdown("---")
if os.path.exists(MAPA_PATH):
    st.sidebar.success("✅ 'Map.png' detectado para la Página 2.")
else:
    st.sidebar.warning("⚠️ No se encontró 'Map.png' en la raíz del proyecto.")

if os.path.exists(CARTEL_PATH):
    st.sidebar.success("✅ 'cartel.png' detectado para la visualización del letrero.")
else:
    st.sidebar.warning("⚠️ No se encontró 'cartel.png' en la raíz del proyecto.")

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

# --- TEXTOS OFICIALES RECONFIGURADOS ---
INFO_ARRIVALS = (
    "1. After passing Mexican Immigration, claim luggage and clear Customs.\n"
    "2. PLEASE DO NOT STOP AT THE TIMESHARE BOOTHS inside the terminal.\n"
    "3. Walk outside: Our official staff is waiting for you under UMBRELLA #4.\n"
    "4. Look for the recognizable transportation sign shown on the right."
)

INFO_POLICIES = (
    "Modifications: Contact us at reservations@casadorada.com at least 24 hours before your service.\n"
    "Departure Pick-ups: The driver will wait a maximum of 10 minutes after the scheduled time.\n"
    "Non-Transferable: This official service is valid exclusively for the registered guest name.\n"
    "Toll Free Assistance: 1-866-448-0151 | Monday to Friday from 8:00 a.m. to 07:00 p.m. (PST)"
)

# --- CLASE PDF ---
class VoucherPDF(FPDF):
    def __init__(self, logo_file=None):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.logo_file = logo_file

    def header(self):
        if self.page_no() == 1:
            # Colocar el Logo en el CENTRO y GRANDE (ancho 70mm, centrado horizontalmente en A4)
            if self.logo_file:
                try:
                    self.image(self.logo_file, 70, 10, 70)
                except Exception:
                    self.set_draw_color(14, 165, 233)
                    self.rect(70, 10, 70, 22)
                    self.set_xy(70, 18)
                    self.set_font("Helvetica", "I", 9)
                    self.set_text_color(100, 116, 139)
                    self.cell(70, 5, "[ Error loading logo ]", align="C")
            else:
                self.set_draw_color(14, 165, 233)
                self.rect(70, 10, 70, 22)
                self.set_xy(70, 18)
                self.set_font("Helvetica", "I", 9)
                self.set_text_color(100, 116, 139)
                self.cell(70, 5, "[ Corporate Travel Alliance ]", align="C")

            # Saludo en la parte IZQUIERDA y en INGLÉS
            self.set_xy(14, 36)
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(2, 132, 199)
            self.cell(0, 8, f"Hello, {nombre_huesped}!", ln=1, align="L")
            
            # Subtítulo en la parte izquierda y en inglés
            self.set_font("Helvetica", "", 10)
            self.set_text_color(100, 116, 139)
            self.cell(0, 5, "We are Corporate Travel Alliance and it will be a pleasure to welcome you.", ln=1, align="L")
            self.ln(5)

    def footer(self):
        if self.page_no() == 1:
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(148, 163, 184)
            self.cell(0, 10, "Corporate Travel Alliance - Page 1/2", align="C")

def crear_pdf():
    pdf = VoucherPDF(logo_file=logo_a_usar)
    pdf.alias_nb_pages()
    
    # --- PÁGINA 1: TARJETA DE BIENVENIDA ---
    pdf.add_page()
    
    # --- BLOQUE CENTRAL: BIENVENIDA AL AEROPUERTO (RECORRIDO HACIA ABAJO -> y=54) ---
    pdf.set_y(54)
    pdf.set_fill_color(240, 249, 255)
    pdf.rect(12, pdf.get_y(), 186, 36, style="F")
    
    pdf.set_xy(16, pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(0, 5, "AIRPORT PROCEDURES - HOW TO FIND US", ln=1)
    
    pdf.set_x(16)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(115, 5.2, INFO_ARRIVALS, border=0, align="L")
    
    # Cuadro del Letrero (Sign Box)
    y_actual = pdf.get_y()
    if os.path.exists(CARTEL_PATH):
        try:
            pdf.image(CARTEL_PATH, x=142, y=y_actual - 26, w=46, h=23)
        except Exception:
            pdf.set_xy(140, y_actual - 25)
            pdf.set_fill_color(255, 255, 255)
            pdf.set_draw_color(14, 165, 233)
            pdf.rect(140, y_actual - 25, 50, 20, style="FD") 
            pdf.set_xy(140, y_actual - 17)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(2, 132, 199)
            pdf.cell(50, 4, "[ Error en cartel.png ]", ln=1, align="C")
    else:
        pdf.set_xy(140, y_actual - 25)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(14, 165, 233)
        pdf.rect(140, y_actual - 25, 50, 20, style="FD") 
        pdf.set_xy(140, y_actual - 20)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(2, 132, 199)
        pdf.cell(50, 4, "TRANSPORTATION SIGN", ln=1, align="C")
        pdf.set_x(140)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(50, 4, "[ Official Logo Here ]", ln=1, align="C")
    
    pdf.set_y(94) # Flujo recorrido hacia abajo
    
    # --- DISEÑO DE TARJETAS DE INFORMACIÓN ---
    def crear_tarjeta_datos(titulo_seccion, datos_dict):
        pdf.set_fill_color(2, 132, 199)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 7, f"   {titulo_seccion}", ln=1, fill=True)
        
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(241, 245, 249)
        
        for key, val in datos_dict.items():
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(65, 8, f"   {key}", border="B", fill=True)
            
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 8, str(val), border="B", ln=1, fill=True)
        pdf.ln(4)

    datos_servicio = {
        "Confirmation Number:": confirmacion,
        "Transfer Type / Servicio:": "Round Trip (Regreso Incluido)" if tipo_viaje == "Round Trip" else "One Way (Solo Llegada)",
        "Guests / Pasajeros:": f"{adultos} Adults / {ninos} Children"
    }
    if requiere_car_seats:
        datos_servicio["Special Add-on:"] = "Complimentary Car Seat Added"
        
    crear_tarjeta_datos("TRIP SUMMARY", datos_servicio)

    datos_llegada = {
        "Arrival Date:": fecha_llegada.strftime('%B %d, %Y'),
        "Flight & Airline:": vuelo_llegada_completo,
        "Estimated Pickup Time (ETA):": f"{hora_llegada.strftime('%H:%M')} HRS"
    }
    crear_tarjeta_datos("ARRIVING DETAILS", datos_llegada)
    
    if tipo_viaje == "Round Trip":
        datos_salida = {
            "Departure Date:": fecha_salida.strftime('%B %d, %Y'),
            "Flight & Airline:": vuelo_salida_completo,
            "Flight Departure Time:": f"{hora_salida.strftime('%H:%M')} HRS",
            "Hotel Pickup Time:": f"{hora_pickup.strftime('%H:%M')} HRS (Please be at the lobby)"
        }
        crear_tarjeta_datos("RETURNING DETAILS", datos_salida)
    
    # --- BLOQUE DE NOTAS Y ASISTENCIA ---
    pdf.set_fill_color(254, 243, 199)
    pdf.set_draw_color(252, 211, 77)
    pdf.rect(12, pdf.get_y(), 186, 24, style="F")
    
    pdf.set_xy(16, pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(180, 83, 9)
    pdf.cell(0, 4.5, "IMPORTANT TRAVELER NOTES", ln=1)
    
    pdf.set_x(16)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(120, 53, 4)
    pdf.multi_cell(178, 4, INFO_POLICIES, border=0, align="L")
    
    # --- PÁGINA 2: MAPA COMPLETO ---
    pdf.add_page()
    if os.path.exists(MAPA_PATH):
        pdf.set_auto_page_break(False, margin=0)
        pdf.image(MAPA_PATH, x=0, y=0, w=210, h=297)
        pdf.set_auto_page_break(True, margin=10)
    else:
        pdf.set_text_color(239, 68, 68)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 20, f"[Error: '{MAPA_PATH}' is missing for full screen rendering]", ln=1, align="C")

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
