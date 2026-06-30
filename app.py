import streamlit as st
import datetime
from fpdf import FPDF
import os

# Streamlit Page Configuration
st.set_page_config(page_title="Corporate Travel Alliance Voucher Generator", layout="centered", page_icon="📋")

st.title("📋 Transportation Voucher Creator")
st.write("Complete the service details to generate the two-page PDF file.")

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

# Configuration lists for time and airline selectors
lista_aerolineas = ["Alaska Airlines", "American Airlines", "Southwest Airlines", "Delta Airlines", "Aeroméxico", "WestJet Airlines"]
horas_lista = [f"{i:02d}" for i in range(24)]
minutos_lista = [f"{i:02d}" for i in range(0, 60, 5)] # 5-minute intervals for quicker selection

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
        
        st.write("Estimated Time of Arrival (ETA)")
        c_hr, c_min = st.columns(2)
        with c_hr:
            h_arr = st.selectbox("Hour", horas_lista, index=12, key="h_arr_sel")
        with c_min:
            m_arr = st.selectbox("Min", minutos_lista, index=0, key="m_arr_sel")
        hora_llegada = datetime.time(int(h_arr), int(m_arr))

    with col3:
        confirmacion = st.text_input("Confirmation Number", placeholder="E.g., CD-98765").upper()
        adultos = st.number_input("Adults", min_value=1, value=2, step=1)
        ninos = st.number_input("Children", min_value=0, value=0, step=1)
        requiere_car_seats = st.checkbox("Require Car Seats?", key="cs_check")

vuelo_llegada_completo = f"{aerolinea_llegada} {num_vuelo_llegada}".strip()

# --- DYNAMIC DEPARTURE SECTION (ROUND TRIP) ---
fecha_salida = None
vuelo_salida_completo = ""
hora_salida = None
hora_pickup = None

if tipo_viaje == "Round Trip":
    with tab2:
        col_dep1, col_dep2, col_dep3 = st.columns(3)
        
        with col_dep1:
            fecha_salida = st.date_input("Departure Date", datetime.date.today() + datetime.timedelta(days=5))
            aerolinea_salida = st.selectbox("Departure Airline", lista_aerolineas, key="air_dep")

        with col_dep2:
            num_vuelo_salida = st.text_input("Departure Flight Number", placeholder="E.g., 1357", key="num_dep")
            vuelo_salida_completo = f"{aerolinea_salida} {num_vuelo_salida}".strip()
            
            st.write("Flight Departure Time")
            c_hr_d, c_min_d = st.columns(2)
            with c_hr_d:
                h_dep = st.selectbox("Hour", horas_lista, index=15, key="h_dep_sel")
            with c_min_d:
                m_dep = st.selectbox("Min", minutos_lista, index=0, key="m_dep_sel")
            hora_salida = datetime.time(int(h_dep), int(m_dep))

        with col_dep3:
            # Auto-calculate default pickup time (3.5 hours before flight departure)
            dt_vuelo = datetime.datetime.combine(datetime.date.today(), hora_salida)
            dt_pickup_default = dt_vuelo - datetime.timedelta(hours=3, minutes=30)
            
            st.write("Scheduled Pick-up Time")
            c_hr_p, c_min_p = st.columns(2)
            with c_hr_p:
                h_pick = st.selectbox("Hour", horas_lista, index=horas_lista.index(f"{dt_pickup_default.hour:02d}"), key="h_pick_sel")
            with c_min_p:
                min_cercano = str(int(5 * round(dt_pickup_default.minute / 5))).zfill(2)
                if min_cercano == "60": 
                    min_cercano = "55"
                min_lista_idx = minutos_lista.index(min_cercano)
                m_pick = st.selectbox("Min", minutos_lista, index=min_lista_idx, key="m_pick_sel")
            
            hora_pickup = datetime.time(int(h_pick), int(m_pick))

st.markdown("---")

INFO_POLICIES = (
    "Modifications: Contact us at reservations@casadorada.com or miriam.cham@casadorada.com at least 24 hours before your service.\n"
    "Departure Pick-ups: The driver will wait a maximum of 10 minutes after the scheduled time.\n"
    "Non-Transferable: This official service is valid exclusively for the registered guest name.\n"
    "Toll Free Assistance: 1-866-448-0151 | Monday to Friday from 8:00 a.m. to 07:00 p.m. (PST)"
)

# --- PDF CLASS WITH INLINE BOLD SUPPORT ---
class VoucherPDF(FPDF):
    def __init__(self, logo_file=None):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.logo_file = logo_file

    def header(self):
        if self.page_no() == 1:
            if self.logo_file:
                try: self.image(self.logo_file, 62.5, 6, 85)
                except Exception: self.placeholder_logo()
            else:
                self.placeholder_logo()

            self.set_xy(14, 56)
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(2, 132, 199)
            self.cell(0, 8, f"Hello, {nombre_huesped}!", ln=1, align="L")
            
            self.set_font("Helvetica", "", 10)
            self.set_text_color(100, 116, 139)
            self.cell(0, 5, "We are Corporate Travel Alliance and it will be a pleasure to welcome you.", ln=1, align="L")
            self.ln(5)

    def placeholder_logo(self):
        self.set_draw_color(14, 165, 233)
        self.rect(62.5, 6, 85, 26)
        self.set_xy(62.5, 16)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 116, 139)
        self.cell(85, 5, "[ Corporate Travel Alliance ]", align="C")

    def footer(self):
        if self.page_no() == 1:
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(148, 163, 184)
            self.cell(0, 10, "Corporate Travel Alliance - Page 1/2", align="C")

    # Auxiliary function to print mixed fonts (Normal and Bold inline text)
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
    pdf.set_y(78)
    pdf.set_fill_color(240, 249, 255)
    pdf.rect(12, pdf.get_y(), 186, 38, style="F")
    
    pdf.set_xy(16, pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(0, 5, "AIRPORT PROCEDURES - HOW TO FIND US", ln=1)
    
    # Render inline bold text requested
    lineas_arrivals = [
        "1. After passing Mexican Immigration, claim luggage and clear Customs.",
        "2. **PLEASE DO NOT STOP AT THE TIMESHARE BOOTHS.**",
        "3. Walk outside: Our official staff is waiting for you **UNDER UMBRELLA #4**.",
        "4. Look for the recognizable transportation sign shown on the right."
    ]
    
    y_linea = pdf.get_y() + 1
    for linea in lineas_arrivals:
        pdf.escribir_linea_mixta(16, y_linea, linea, 5.2)
        y_linea += 5.2
        
    if os.path.exists(CARTEL_PATH):
        try: pdf.image(CARTEL_PATH, x=144, y=79, w=45, h=0)
        except Exception: pass

    # Data Summary Sections
    pdf.set_y(124)
    
    def crear_tarjeta_datos(titulo_seccion, datos_dict):
        pdf.set_fill_color(2, 132, 199)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 7.5, f"   {titulo_seccion}", ln=1, fill=True)
        
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(241, 245, 249)
        
        for key, val in datos_dict.items():
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(65, 8.5, f"   {key}", border="B", fill=True)
            
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 8.5, str(val), border="B", ln=1, fill=True)
        pdf.ln(8)

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
    
    # --- IMPORTANT NOTES & POLICIES BLOCK ---
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
