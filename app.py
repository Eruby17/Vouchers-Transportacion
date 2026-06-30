import streamlit as st
import datetime
from fpdf import FPDF
import os

# Streamlit Page Configuration
st.set_page_config(page_title="Corporate Travel Alliance Voucher Generator", layout="centered", page_icon="📋")

st.title("📋 Transportation Voucher Creator")
st.write("Complete the service details to generate the compressed PDF file.")

# --- STATIC FILES ---
MAPA_PATH = "Map.png"
LOGO_DEFAULT_PATH = "logo.jpeg"
CARTEL_PATH = "cartel.png"

# Automatically determine which logo to use
logo_a_usar = LOGO_DEFAULT_PATH if os.path.exists(LOGO_DEFAULT_PATH) else None
if logo_a_usar:
    st.success("✅ 'logo.jpeg' detected and loaded automatically.")
else:
    st.info("ℹ️ The voucher will be generated with a blank logo space (add 'logo.jpeg' to the root directory to activate it).")

# --- MAIN FORM ---
st.subheader("Service Information")

# Service Type Selection
tipo_viaje = st.radio("Service Type", ["One Way (Arrival Only)", "Round Trip"], horizontal=True)

lista_aerolineas = ["Alaska Airlines", "American Airlines", "Southwest Airlines", "Delta Airlines", "Aeroméxico", "WestJet Airlines"]

# Organize layout using tabs
if tipo_viaje == "Round Trip":
    tab1, tab2 = st.tabs(["🛬 Arrival Information", "🛫 Departure Information"])
else:
    tab1 = st.tabs(["🛬 Arrival Information"])[0]

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_input = st.text_input("Guest Name (You can paste in UPPERCASE)", placeholder="E.g., ALFREDO RIVERA")
        nombre_huesped = nombre_input.strip().title()
        fecha_llegada = st.date_input("Arrival Date", datetime.date.today())
    
    with col2:
        aerolinea_llegada = st.selectbox("Arrival Airline", lista_aerolineas, key="air_arr")
        num_vuelo_llegada = st.text_input("Arrival Flight Number", placeholder="E.g., 2468", key="num_arr")
        
        # Clean Text Input for Time instead of multiple selectboxes
        hora_llegada_str = st.text_input("Estimated Time of Arrival (ETA)", value="12:00", placeholder="HH:MM (24h format)")
        try:
            h_arr, m_arr = map(int, hora_llegada_str.split(":"))
            hora_llegada = datetime.time(h_arr, m_arr)
        except ValueError:
            st.error("Invalid Arrival Time format. Using 12:00 as fallback.")
            hora_llegada = datetime.time(12, 0)

    with col3:
        confirmacion = st.text_input("Confirmation Number", placeholder="E.g., CD-98765").upper()
        adultos = st.number_input("Adults", min_value=1, value=2, step=1)
        ninos = st.number_input("Children", min_value=0, value=0, step=1)
        requiere_car_seats = st.checkbox("Require Car Seats?", key="cs_check")

vuelo_llegada_completo = f"{aerolinea_llegada} {num_vuelo_llegada}".strip()

# --- DYNAMIC DEPARTURE SECTION (ROUND TRIP) ---
fecha_salida = None
vuelo_salida_completo = ""
hora_salida = datetime.time(15, 0)
hora_pickup = datetime.time(11, 30)

if tipo_viaje == "Round Trip":
    with tab2:
        col_dep1, col_dep2, col_dep3 = st.columns(3)
        
        with col_dep1:
            fecha_salida = st.date_input("Departure Date", datetime.date.today() + datetime.timedelta(days=5))
            aerolinea_salida = st.selectbox("Departure Airline", lista_aerolineas, key="air_dep")

        with col_dep2:
            num_vuelo_salida = st.text_input("Departure Flight Number", placeholder="E.g., 1357", key="num_dep")
            vuelo_salida_completo = f"{aerolinea_salida} {num_vuelo_salida}".strip()
            
            hora_salida_str = st.text_input("Flight Departure Time", value="15:00", placeholder="HH:MM (24h format)")
            try:
                h_dep, m_dep = map(int, hora_salida_str.split(":"))
                hora_salida = datetime.time(h_dep, m_dep)
            except ValueError:
                st.error("Invalid Departure Time format. Using 15:00 as fallback.")
                hora_salida = datetime.time(15, 0)

        with col_dep3:
            # 1. Automatic calculation: Exactly 3.5 hours before flight departure
            dt_vuelo = datetime.datetime.combine(datetime.date.today(), hora_salida)
            dt_pickup_auto = dt_vuelo - datetime.timedelta(hours=3, minutes=30)
            hora_auto_str = dt_pickup_auto.strftime('%H:%M')
            
            # 2. Checkbox option to enable manual override
            custom_pickup = st.checkbox("Customize Pick-up Time Manually")
            
            if custom_pickup:
                hora_pickup_str = st.text_input("Scheduled Pick-up Time", value=hora_auto_str, placeholder="HH:MM (24h format)")
            else:
                st.text_input("Scheduled Pick-up Time (Auto-calculated)", value=hora_auto_str, disabled=True)
                hora_pickup_str = hora_auto_str
                
            try:
                h_pick, m_pick = map(int, hora_pickup_str.split(":"))
                hora_pickup = datetime.time(h_pick, m_pick)
            except ValueError:
                hora_pickup = dt_pickup_auto.time()

st.markdown("---")

INFO_POLICIES = (
    "Modifications: Contact us at reservations@casadorada.com or miriam.cham@casadorada.com at least 24 hours before your service.\n"
    "Departure Pick-ups: The driver will wait a maximum of 10 minutes after the scheduled time.\n"
    "Non-Transferable: This official service is valid exclusively for the registered guest name.\n"
    "Toll Free Assistance: 1-866-448-0151 | Monday to Friday from 8:00 a.m. to 07:00 p.m. (PST)"
)

# --- COMPRESSED PDF CLASS WITH ANTI-OVERLAP LOGIC ---
class VoucherPDF(FPDF):
    def __init__(self, logo_file=None):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.logo_file = logo_file

    def header(self):
        if self.page_no() == 1:
            # Shifted logo to the absolute top edge (y=1) and made it slightly sleeker
            if self.logo_file:
                try: 
                    self.image(self.logo_file, x=62.5, y=1, w=85, h=22)
                    ultimo_y_logo = 24
                except Exception: 
                    self.placeholder_logo()
                    ultimo_y_logo = 25
            else:
                self.placeholder_logo()
                ultimo_y_logo = 25

            # Dynamic positioning: Starts exactly below the logo to prevent overlap
            self.set_xy(14, ultimo_y_logo + 4)
            self.set_font("Helvetica", "B", 17)
            self.set_text_color(2, 132, 199)
            self.cell(0, 7, f"Hello, {nombre_huesped}!", ln=1, align="L")
            
            self.set_font("Helvetica", "", 9.5)
            self.set_text_color(100, 116, 139)
            self.cell(0, 4, "We are Corporate Travel Alliance and it will be a pleasure to welcome you.", ln=1, align="L")
            self.ln(1)

    def placeholder_logo(self):
        self.set_draw_color(14, 165, 233)
        self.rect(62.5, 1, 85, 20)
        self.set_xy(62.5, 9)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 116, 139)
        self.cell(85, 5, "[ Corporate Travel Alliance ]", align="C")

    def footer(self):
        if self.page_no() == 1:
            self.set_y(-10)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(148, 163, 184)
            self.cell(0, 10, "Corporate Travel Alliance - Page 1/2", align="C")

    def escribir_linea_mixta(self, x, y, texto_linea, alto_celda):
        self.set_xy(x, y)
        segmentos = texto_linea.split("**")
        es_negrita = False
        
        for segmento in segmentos:
            if es_negrita:
                self.set_font("Helvetica", "B", 9.5)
                self.set_text_color(15, 23, 42)
            else:
                self.set_font("Helvetica", "", 9.5)
                self.set_text_color(51, 65, 85)
            
            ancho_texto = self.get_string_width(segmento)
            self.cell(ancho_texto, alto_celda, segmento, border=0)
            self.set_x(self.get_x())
            es_negrita = not es_negrita

def crear_pdf():
    pdf = VoucherPDF(logo_file=logo_a_usar)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # --- CENTRAL BLOCK: AIRPORT PROCEDURES ---
    pdf.set_y(44)
    pdf.set_fill_color(240, 249, 255)
    pdf.rect(12, pdf.get_y(), 186, 36, style="F")
    
    pdf.set_xy(16, pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(0, 5, "AIRPORT PROCEDURES - HOW TO FIND US", ln=1)
    
    lineas_arrivals = [
        "1. After passing Mexican Immigration, claim luggage and clear Customs.",
        "2. **PLEASE DO NOT STOP AT THE TIMESHARE BOOTHS.**",
        "3. Walk outside: Our official staff is waiting for you **UNDER UMBRELLA #4**.",
        "4. Look for the recognizable transportation sign shown on the right."
    ]
    
    y_linea = pdf.get_y() + 1
    for linea in lineas_arrivals:
        pdf.escribir_linea_mixta(16, y_linea, linea, 5.0)
        y_linea += 5.0
        
    if os.path.exists(CARTEL_PATH):
        try: pdf.image(CARTEL_PATH, x=146, y=45, w=41, h=0)
        except Exception: pass

    # Data Summary Sections
    pdf.set_y(85)
    
    def crear_tarjeta_datos(titulo_seccion, datos_dict):
        pdf.set_fill_color(2, 132, 199)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 6.5, f"   {titulo_seccion}", ln=1, fill=True)
        
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(241, 245, 249)
        
        for key, val in datos_dict.items():
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(65, 6.8, f"   {key}", border="B", fill=True)
            
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 6.8, str(val), border="B", ln=1, fill=True)
        pdf.ln(3.5)

    datos_servicio = {
        "Confirmation Number:": confirmacion,
        "Transfer Type:": "Round Trip" if tipo_viaje == "Round Trip" else "One Way",
        "Passengers:": f"{adultos} Adults / {ninos} Children"
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
    
    # --- OPTIMIZED AND LARGER POLICIES/NOTES BLOCK ---
    # Increased text size from 8 to 9, line spacing to 4.5. Box size adapted to 27mm.
    pdf.set_fill_color(246, 247, 249)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(12, pdf.get_y() + 1, 186, 27, style="F")
    
    pdf.set_xy(16, pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 4.5, "IMPORTANT TRAVELER NOTES", ln=1)
    
    pdf.set_x(16)
    pdf.set_font("Helvetica", "", 9)  # Font size bumped up to 9pt for high legibility
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(178, 4.5, INFO_POLICIES, border=0, align="L")
    
    # --- PAGE 2: FULL SCREEN MAP ---
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

# --- ACTION PROCESSING BUTTON ---
st.markdown("### Process and Generate")
if st.button("🚀 Generate PDF Voucher", type="primary", use_container_width=True):
    if not nombre_input:
        st.error("Please enter the guest name.")
    elif not confirmacion or not num_vuelo_llegada:
        st.error("Please complete the required fields (Confirmation Number and Flight Number) before proceeding.")
    elif tipo_viaje == "Round Trip" and not num_vuelo_salida:
        st.error("Please enter the departure flight number for Round Trip service.")
    else:
        try:
            pdf_data = bytes(crear_pdf())
            st.success("Voucher successfully generated!")
            
            st.download_button(
                label="📥 Download PDF Voucher",
                data=pdf_data,
                file_name=f"Voucher_{confirmacion}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Technical error during PDF compilation: {e}")
