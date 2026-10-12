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

# Opción de Aeropuerto Privado CSL en la barra lateral
csl_private = st.sidebar.checkbox("🛩️ CSL Private Airport / Aeropuerto Privado CSL", value=False)

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

# --- SESSION STATE & RESET ---
if "guest_name" not in st.session_state:
    st.session_state["guest_name"] = ""
if "conf_num" not in st.session_state:
    st.session_state["conf_num"] = ""
if "fl_arr" not in st.session_state:
    st.session_state["fl_arr"] = ""
if "fl_dep" not in st.session_state:
    st.session_state["fl_dep"] = ""
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
    st.session_state["cs_check"] = False
    st.session_state["gs_check"] = False
    st.session_state["adults_count"] = 2
    st.session_state["children_count"] = 0
    st.session_state["time_arr_val"] = "12:00"
    st.session_state["time_dep_val"] = "15:00"
    st.session_state["date_arr_val"] = datetime.date.today()
    st.session_state["date_dep_val"] = datetime.date.today() + datetime.timedelta(days=4)

st.sidebar.button(t["reset"], on_click=reset_form, use_container_width=True)

st.title(t["title"])
st.write(t["desc"])

# --- STATIC FILES ---
LOGO_DEFAULT_PATH = "logo.jpeg"
CARTEL_PATH = "cartel.png"
logo_a_usar = LOGO_DEFAULT_PATH if os.path.exists(LOGO_DEFAULT_PATH) else None

# --- MAIN FORM ---
st.subheader(t["sub_info"])

tipo_viaje = st.radio(t["type"], [t["ow_arr"], t["ow_dep"], t["rt"]], horizontal=True)

# Se agrega JSX a la lista de aerolíneas
lista_aerolineas = ["Air Canada", "Aeroméxico", "Alaska Airlines", "American Airlines", "Delta Airlines", "United Airlines", "Frontier Airlines", "Jet Blue Airlines", "JSX", "Southwest Airlines", "Viva Aerobus", "Volaris", "WestJet Airlines", "Private Jet"]

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
            aerolinea_llegada = st.selectbox(t["airline_arr"], lista_aerolineas, key="air_arr")
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
                terminal_seleccionada = st.selectbox(t["term"], ["Terminal 2", "Terminal 1"], index=0)
            
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
            
            if tipo_viaje == t["rt"] and 'aerolinea_llegada' in locals():
                default_idx = lista_aerolineas.index(aerolinea_llegada) if aerolinea_llegada in lista_aerolineas else 0
                aerolinea_salida = st.selectbox(t["airline_dep"], lista_aerolineas, index=default_idx, key=f"air_dep_{aerolinea_llegada}")
            else:
                aerolinea_salida = st.selectbox(t["airline_dep"], lista_aerolineas, key="air_dep_standalone")

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
            
            custom_pickup = st.checkbox(t["custom_p"])
            
            if custom_pickup:
                hora_pickup_str = st.text_input(t["p_manual"], value=hora_auto_str)
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

def crear_pdf(terminal):
    pdf = VoucherPDF(logo_file=logo_a_usar)
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

# --- BUTTON ACTION PROCESSING ---
st.markdown(t["btn_process"])

if st.button(t["btn_gen"], type="primary", use_container_width=True):
    if not nombre_input:
        st.error(t["err_name"])
    elif not confirmacion:
        st.error(t["err_req"])
    elif tipo_viaje == t["rt"] and not num_vuelo_salida:
        st.error(t["err_dep"])
    else:
        try:
            pdf_raw = crear_pdf(terminal_seleccionada)
            pdf_data = bytes(pdf_raw, 'latin-1') 
            
            st.success(t["success"])
            
            if tipo_viaje == t["rt"]:
                tag_viaje = "Roundtrip"
            elif tipo_viaje == t["ow_dep"]:
                tag_viaje = "Departure"
            else:
                tag_viaje = "One Way"
                
            nombre_archivo_pdf = f"{tag_viaje} Transportation voucher- {confirmacion}- {nombre_huesped}.pdf"
            
            # -------------------------------------
            # VISTA PREVIA DEL VOUCHER PDF
            # -------------------------------------

            st.subheader(
                "PDF Preview"
                if idioma == "English"
                else "Vista previa del PDF"
            )

            st.pdf(
                pdf_data,
                height=700
            )

            # -------------------------------------
            # DESCARGAR VOUCHER
            # -------------------------------------

            st.download_button(
                label=t["btn_dl"],
                data=pdf_data,
                file_name=nombre_archivo_pdf,
                mime="application/pdf",
                use_container_width=True
            )

            st.info(
                "Para limpiar el formulario para un nuevo cliente, haz clic en el botón 'Limpiar Formulario' en la barra izquierda."
                if idioma != "English"
                else "To clear the form for a new client, click 'Reset Form' on the left sidebar."
            )

        except Exception as e:
            st.error(
                f"Technical error during PDF compilation: {e}"
                if idioma == "English"
                else f"Error técnico durante la compilación del PDF: {e}"
            )
