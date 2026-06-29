import streamlit as st
import datetime
from fpdf import FPDF
import os

# Configuración de la página en Streamlit
st.set_page_config(page_title="Generador de Vouchers Casa Dorada", layout="wide", page_icon="📋")

st.title("📋 Creador de Vouchers de Transportación — Casa Dorada")
st.write("Completa los datos del servicio para generar el archivo PDF de dos páginas.")

# --- ARCHIVOS ESTÁTICOS ---
MAPA_PATH = "Map.png" # Nombre corregido a 'Map.png'

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración del Logo")

# BOTÓN PARA INSERTAR EL LOGO DESPUÉS (Carga manual desde la app)
logo_subido = st.sidebar.file_uploader("Subir Logo de la Empresa (PNG o JPG)", type=["png", "jpg", "jpeg"])

if logo_subido:
    st.sidebar.success("✅ Logo cargado para este voucher.")
    st.sidebar.image(logo_subido, caption="Vista previa del logo", use_container_width=True)
else:
    st.sidebar.info("ℹ️ No has subido un logo. El voucher se generará solo con texto en la cabecera.")

st.sidebar.markdown("---")
if os.path.exists(MAPA_PATH):
    st.sidebar.success("✅ 'Map.png' detectado para la Página 2.")
else:
    st.sidebar.warning("⚠️ No se encontró 'Map.png' en la raíz de GitHub. Recuerda subirlo con ese nombre exacto.")

# --- FORMULARIO PRINCIPAL ---
st.subheader("Datos del Servicio")
col1, col2, col3 = st.columns(3)

with col1:
    fecha = st.date_input("Fecha de Llegada", datetime.date.today())
    num_vuelo = st.text_input("Número de Vuelo", placeholder="Ej: AA 214").upper()
    hora_llegada = st.time_input("Hora de Llegada")

with col2:
    confirmacion = st.text_input("Número de Confirmación", placeholder="Ej: CD-98765").upper()
    adultos = st.number_input("Adultos", min_value=1, value=2, step=1)
    ninos = st.number_input("Niños", min_value=0, value=0, step=1)

with col3:
    requiere_car_seats = st.checkbox("¿Requiere Car Seats?")
    if requiere_car_seats:
        cant_car_seats = st.number_input("¿Cuántos?", min_value=1, max_value=4, value=1)
        tipo_car_seat = st.selectbox("Tipo", ["Baby Capsule", "Convertible", "Booster"])
    else:
        cant_car_seats = 0
        tipo_car_seat = "N/A"

st.markdown("---")

# --- TEXTOS OFICIALES DEL VOUCHER ---
INFO_ARRIVALS = (
    "AIRPORT PROCEDURES FOR YOUR ARRIVAL:\n"
    "After passing Mexican Immigration, claim checked luggage and clear Customs, "
    "PLEASE DON'T STOP WITH TIMESHARED BOOTH, THEY WILL TRY TO SELL TRANSPORTATION and "
    "REMEMBER OUR STAFF WILL BE HOLDING A SIGN WITH THE TRANSPORTATION COMPANY LOGO. "
    "ONCE OUT OUR STAFF IS UNDER UMBRELLA # 4 WHERE WILL BE WAITING FOR YOU."
)

INFO_POLICIES = (
    "IMPORTANT POLICIES & CONTACT INFO:\n\n"
    "• For any modifications, you must contact us directly at reservations@casadorada.com and "
    "reservationscd@casadorada.com. Any modifications require to be asked for and confirmed "
    "at least 24 hours before the service.\n\n"
    "• Please be aware that for departures, the driver will wait up to 10 additional minutes "
    "from the scheduled pick-up time. After this time, the driver will have to leave the "
    "hotel, and the company will not be able to provide a refund.\n\n"
    "• Please be advised that the transportation service is arranged by the name of guest reservation. "
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
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} — Casa Dorada Resort & Spa", align="C")

def crear_pdf():
    pdf = VoucherPDF(logo_file=logo_subido)
    pdf.alias_nb_pages()
    
    # --- PÁGINA 1: DATOS Y PROCEDIMIENTO DE LLEGADA ---
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "RESERVATION DETAILS", ln=1)
    pdf.line(10, 38, 200, 38)
    pdf.ln(3)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(60, 8, f"Confirmation Number:", font_style="B")
    pdf.cell(0, 8, f"{confirmacion}", ln=1)
    
    pdf.cell(60, 8, f"Arrival Date:", font_style="B")
    pdf.cell(0, 8, f"{fecha.strftime('%B %d, %Y')}", ln=1)
    
    pdf.cell(60, 8, f"Flight Number:", font_style="B")
    pdf.cell(0, 8, f"{num_vuelo}", ln=1)
    
    pdf.cell(60, 8, f"Estimated Time of Arrival:", font_style="B")
    pdf.cell(0, 8, f"{hora_llegada.strftime('%H:%M')} HRS", ln=1)
    
    pdf.cell(60, 8, f"Passengers:", font_style="B")
    pdf.cell(0, 8, f"{adultos} Adults / {ninos} Children", ln=1)
    
    if requiere_car_seats:
        pdf.cell(60, 8, f"Special Request:", font_style="B")
        pdf.cell(0, 8, f"{cant_car_seats} Car Seat(s) ({tipo_car_seat})", ln=1)
    
    pdf.ln(12)
    
    # Recuadro de Alerta (Sombrilla #4 y advertencias)
    pdf.set_fill_color(255, 242, 204)
    pdf.set_text_color(150, 80, 0)
    pdf.set_font("Helvetica", "B", 11)
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
    if not confirmacion or not num_vuelo:
        st.error("Por favor completa los campos obligatorios (Confirmación y Vuelo) antes de continuar.")
    else:
        try:
            pdf_data = crear_pdf()
            st.success("¡Voucher generado con éxito!")
            
            st.download_button(
                label="📥 Descargar Voucher (PDF)",
                data=pdf_data,
                file_name=f"Voucher_{confirmacion}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error técnico al compilar el PDF: {e}")