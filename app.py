# src/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

# Agregar el directorio src al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Importar módulos de la plataforma
from modules.dashboard import DashboardModule
from modules.sales_copilot import SalesCopilotModule
from modules.data_connectors import DataConnectorsModule
from modules.reporting import ReportingModule
from modules.alerts import AlertsModule

# Configuración de la página
st.set_page_config(
    page_title="Business Intelligence Platform",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Cargar CSS personalizado
def load_css():
    with open("src/assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🚀 Business Intelligence Platform</h1>
    <h3>Plataforma Unificada de Inteligencia Comercial</h3>
    <p>Integración completa de datos, IA y automatización para equipos B2B</p>
</div>
""", unsafe_allow_html=True)

# Inicializar módulos
@st.cache_resource
def init_modules():
    return {
        'dashboard': DashboardModule(),
        'sales_copilot': SalesCopilotModule(),
        'data_connectors': DataConnectorsModule(),
        'reporting': ReportingModule(),
        'alerts': AlertsModule()
    }

modules = init_modules()

# Sidebar para navegación y configuración
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/667eea/ffffff?text=BI+Platform", width=150)
    
    st.markdown("### 🔧 Configuración")
    
    # Selector de módulo principal
    app_mode = st.selectbox(
        "Navegación Principal:",
        ["🏠 Dashboard", "🤖 Sales Copilot", "🔗 Conectores", "📊 Reportes", "🔔 Alertas", "⚙️ Configuración"]
    )
    
    # Configuración de API Keys
    with st.expander("🔑 Configuración API"):
        openai_key = st.text_input("OpenAI API Key:", type="password")
        if openai_key:
            st.session_state.openai_key = openai_key
            st.success("✅ API Key configurada")
    
    # Información del sistema
    st.markdown("---")
    st.markdown("### 📊 Estado del Sistema")
    st.metric("Módulos Activos", "5/5")
    st.metric("Datos Cargados", "✓" if 'df' in st.session_state else "✗")
    st.metric("Última Actualización", datetime.now().strftime("%H:%M"))

# Navegación principal
if app_mode == "🏠 Dashboard":
    modules['dashboard'].render()
    
elif app_mode == "🤖 Sales Copilot":
    modules['sales_copilot'].render()
    
elif app_mode == "🔗 Conectores":
    modules['data_connectors'].render()
    
elif app_mode == "📊 Reportes":
    modules['reporting'].render()
    
elif app_mode == "🔔 Alertas":
    modules['alerts'].render()
    
else:  # Configuración
    st.header("⚙️ Configuración de la Plataforma")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configuración General")
        company_name = st.text_input("Nombre de la Empresa:", value="TechSolutions MX")
        timezone = st.selectbox("Zona Horaria:", ["America/Mexico_City", "UTC", "US/Eastern"])
        currency = st.selectbox("Moneda:", ["MXN", "USD", "EUR"])
        
        st.subheader("Integraciones")
        crm_enabled = st.checkbox("Conectar con CRM")
        sheets_enabled = st.checkbox("Conectar con Google Sheets")
        email_enabled = st.checkbox("Habilitar Email Automation")
    
    with col2:
        st.subheader("Preferencias de Reportes")
        report_frequency = st.selectbox("Frecuencia de Reportes:", ["Diario", "Semanal", "Mensual"])
        auto_export = st.checkbox("Exportación Automática", value=True)
        alert_threshold = st.slider("Umbral de Alertas (%)", 0, 100, 10)
        
        st.subheader("Backup y Seguridad")
        auto_backup = st.checkbox("Backup Automático", value=True)
        data_retention = st.selectbox("Retención de Datos:", ["30 días", "90 días", "1 año", "Indefinido"])

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Business Intelligence Platform</strong> • v1.0 • Desarrollado por Omar Cordero</p>
    <p>Transformando datos en decisiones inteligentes 🚀</p>
</div>
""", unsafe_allow_html=True)

# Inicializar session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'modules_initialized' not in st.session_state:
    st.session_state.modules_initialized = True