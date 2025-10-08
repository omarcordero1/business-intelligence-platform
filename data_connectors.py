# src/modules/data_connectors.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import requests
import json

class DataConnectorsModule:
    def __init__(self):
        self.name = "Data Connectors"
        self.version = "1.0"
        self.connected_sources = []
    
    def render(self):
        st.header("🔗 Conectores de Datos")
        st.markdown("Conecta y unifica datos de múltiples fuentes para tu análisis")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📁 Archivos", "🌐 APIs", "🗄️ Base de Datos", "🔗 Conexiones Activas"])
        
        with tab1:
            self._render_file_connectors()
        with tab2:
            self._render_api_connectors()
        with tab3:
            self._render_database_connectors()
        with tab4:
            self._render_active_connections()
    
    def _render_file_connectors(self):
        """Conectores para archivos locales"""
        st.subheader("📁 Cargar Archivos Locales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Subir Archivo**")
            file_type = st.radio("Tipo de archivo:", ["CSV", "Excel", "JSON"])
            
            uploaded_file = st.file_uploader(
                f"Selecciona archivo {file_type}",
                type=['csv', 'xlsx', 'json'],
                help="Formatos soportados: CSV, Excel, JSON"
            )
            
            if uploaded_file:
                try:
                    if file_type == "CSV":
                        df = pd.read_csv(uploaded_file)
                    elif file_type == "Excel":
                        df = pd.read_excel(uploaded_file)
                    else:  # JSON
                        df = pd.read_json(uploaded_file)
                    
                    # Procesar datos
                    df = self._process_uploaded_data(df)
                    st.session_state.df = df
                    
                    st.success(f"✅ {uploaded_file.name} cargado - {len(df)} registros")
                    
                    # Mostrar preview
                    with st.expander("🔍 Vista previa de datos"):
                        st.dataframe(df.head(10), use_container_width=True)
                        st.write(f"**Columnas:** {list(df.columns)}")
                        st.write(f"**Registros:** {len(df)}")
                        
                except Exception as e:
                    st.error(f"❌ Error cargando archivo: {str(e)}")
        
        with col2:
            st.write("**Datos de Ejemplo**")
            st.info("Usa datos de ejemplo para explorar la plataforma")
            
            if st.button("🎯 Generar Datos de Ejemplo", type="primary"):
                df = self._generate_sample_data()
                st.session_state.df = df
                st.success("✅ Datos de ejemplo generados - 500 registros")
                
                with st.expander("🔍 Ver datos de ejemplo"):
                    st.dataframe(df.head(10), use_container_width=True)
            
            st.write("**Exportar Datos**")
            if st.session_state.get('df') is not None:
                if st.button("📤 Exportar Datos Procesados"):
                    csv = st.session_state.df.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"datos_procesados_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
    
    def _process_uploaded_data(self, df):
        """Procesar datos subidos"""
        # Estandarizar nombres de columnas
        column_mapping = {
            'fecha': ['fecha', 'date', 'fecha_venta', 'timestamp'],
            'cliente': ['cliente', 'client', 'customer', 'empresa'],
            'producto_servicio': ['producto_servicio', 'producto', 'servicio', 'product', 'service'],
            'monto_venta': ['monto_venta', 'venta', 'monto', 'sales', 'amount', 'valor'],
            'vendedor': ['vendedor', 'seller', 'sales_rep', 'ejecutivo'],
            'region': ['region', 'zona', 'territory', 'area'],
            'costo': ['costo', 'cost', 'costo_venta'],
            'comision': ['comision', 'commission']
        }
        
        for standard_name, alternatives in column_mapping.items():
            for alt_name in alternatives:
                if alt_name in df.columns and standard_name not in df.columns:
                    df[standard_name] = df[alt_name]
                    break
        
        # Convertir fecha si existe
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        
        # Asegurar que monto_venta es numérico
        if 'monto_venta' in df.columns:
            df['monto_venta'] = pd.to_numeric(df['monto_venta'], errors='coerce')
        
        return df
    
    def _generate_sample_data(self):
        """Generar datos de ejemplo realistas"""
        np.random.seed(42)
        
        # Fechas de los últimos 12 meses
        start_date = datetime.now() - timedelta(days=365)
        dates = pd.date_range(start_date, periods=365, freq='D')
        
        # Datos de ejemplo
        sample_data = {
            'fecha': np.random.choice(dates, 500),
            'cliente': np.random.choice([
                'TechSolutions SA', 'CloudCorp MX', 'DataDriven Inc', 'InnovateLabs',
                'DigitalFlow', 'SmartSystems', 'NextGen Tech', 'FutureWorks',
                'MetaSystems', 'AI Ventures', 'BlockChain MX', 'CyberSecure',
                'DataLabs', 'CloudInnovate', 'TechGrowth', 'DigitalFuture'
            ], 500),
            'producto_servicio': np.random.choice([
                'SaaS Enterprise', 'Consultoría Cloud', 'Implementación',
                'Soporte Premium', 'Capacitación', 'Desarrollo Custom',
                'Auditoría Security', 'Migración Digital', 'Analytics Avanzado'
            ], 500, p=[0.25, 0.18, 0.15, 0.12, 0.1, 0.08, 0.06, 0.04, 0.02]),
            'monto_venta': np.random.lognormal(10, 0.8, 500).round(2),
            'vendedor': np.random.choice([
                'Omar Cordero', 'Ana López', 'Carlos Ruiz', 'María García', 
                'Juan Díaz', 'Laura Martínez', 'Pedro Hernández'
            ], 500, p=[0.25, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05]),
            'region': np.random.choice(['Norte', 'Centro', 'Sur', 'Internacional'], 500, p=[0.4, 0.3, 0.2, 0.1]),
            'industria': np.random.choice(['Tecnología', 'Finanzas', 'Manufactura', 'Salud', 'Retail', 'Educación'], 500),
            'estado_venta': np.random.choice(['Completado', 'En proceso', 'Cotización'], 500, p=[0.7, 0.2, 0.1]),
            'costo': np.random.lognormal(9, 0.7, 500).round(2),
        }
        
        df = pd.DataFrame(sample_data)
        df['comision'] = (df['monto_venta'] * np.random.uniform(0.08, 0.12, 500)).round(2)
        df['utilidad'] = df['monto_venta'] - df['costo']
        df['margen'] = (df['utilidad'] / df['monto_venta'] * 100).round(2)
        
        return df
    
    def _render_api_connectors(self):
        """Conectores para APIs externas"""
        st.subheader("🌐 Conectar con APIs Externas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔗 CRM Integration**")
            crm_type = st.selectbox("Tipo de CRM:", ["Salesforce", "HubSpot", "Zoho", "Custom API"])
            
            if crm_type != "Custom API":
                st.info(f"Conector {crm_type} - En desarrollo")
            else:
                api_url = st.text_input("URL de API:")
                api_key = st.text_input("API Key:", type="password")
                endpoint = st.text_input("Endpoint:", value="/api/v1/sales")
                
                if st.button("🔌 Conectar a CRM"):
                    st.success("✅ Conexión CRM configurada (simulación)")
                    self.connected_sources.append(f"CRM - {crm_type}")
            
            st.write("**📊 Google Sheets**")
            sheet_url = st.text_input("URL de Google Sheets:")
            if st.button("📋 Conectar Google Sheets"):
                st.success("✅ Google Sheets conectado (simulación)")
                self.connected_sources.append("Google Sheets")
        
        with col2:
            st.write("**💼 LinkedIn Sales Navigator**")
            st.info("Conector LinkedIn - En desarrollo")
            
            st.write("**📧 Email Marketing**")
            email_service = st.selectbox("Servicio de Email:", ["Mailchimp", "SendGrid", "ActiveCampaign", "Custom"])
            if st.button("📨 Conectar Email"):
                st.success("✅ Servicio de email conectado (simulación)")
                self.connected_sources.append(f"Email - {email_service}")
            
            st.write("**🔔 Slack Integration**")
            slack_webhook = st.text_input("Webhook de Slack:")
            if st.button("💬 Conectar Slack"):
                st.success("✅ Slack conectado (simulación)")
                self.connected_sources.append("Slack")
    
    def _render_database_connectors(self):
        """Conectores para bases de datos"""
        st.subheader("🗄️ Conexión a Base de Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Configuración de Base de Datos**")
            
            db_type = st.selectbox("Tipo de Base de Datos:", 
                                 ["PostgreSQL", "MySQL", "SQLite", "SQL Server"])
            
            if db_type != "SQLite":
                host = st.text_input("Host:", value="localhost")
                port = st.number_input("Puerto:", value=5432)
                database = st.text_input("Base de Datos:", value="sales_data")
                username = st.text_input("Usuario:")
                password = st.text_input("Contraseña:", type="password")
            else:
                db_file = st.file_uploader("Archivo SQLite:", type=['db', 'sqlite'])
            
            table_name = st.text_input("Nombre de Tabla:", value="ventas")
            
            if st.button("🗃️ Conectar Base de Datos"):
                st.success("✅ Conexión a base de datos configurada (simulación)")
                self.connected_sources.append(f"DB - {db_type}")
        
        with col2:
            st.write("**Consulta Personalizada**")
            
            sql_query = st.text_area(
                "Consulta SQL:",
                value="SELECT * FROM ventas WHERE fecha >= CURRENT_DATE - INTERVAL '30 days'",
                height=100
            )
            
            if st.button("🔍 Ejecutar Consulta"):
                st.info("Ejecutando consulta... (simulación)")
                
                # Simular datos de la consulta
                df_simulated = self._generate_sample_data().head(50)
                st.session_state.df = df_simulated
                st.success(f"✅ Consulta ejecutada - {len(df_simulated)} registros")
                
                with st.expander("🔍 Ver resultados"):
                    st.dataframe(df_simulated, use_container_width=True)
            
            st.write("**Sincronización Automática**")
            sync_frequency = st.selectbox("Frecuencia de Sincronización:", 
                                        ["Manual", "Diaria", "Semanal", "Mensual"])
            if st.button("🔄 Programar Sincronización"):
                st.success(f"✅ Sincronización {sync_frequency.lower()} programada")
    
    def _render_active_connections(self):
        """Mostrar conexiones activas"""
        st.subheader("🔗 Conexiones Activas")
        
        if not self.connected_sources:
            st.info("ℹ️ No hay conexiones activas. Configura conectores en las pestañas anteriores.")
            return
        
        st.success(f"✅ {len(self.connected_sources)} conexiones activas")
        
        for i, connection in enumerate(self.connected_sources, 1):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{i}. {connection}**")
                st.write(f"🟢 Conectado - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                if st.button("🔄 Sincronizar", key=f"sync_{i}"):
                    st.success(f"✅ {connection} sincronizado")
            
            with col3:
                if st.button("❌ Desconectar", key=f"disconnect_{i}"):
                    self.connected_sources.remove(connection)
                    st.rerun()
        
        # Estadísticas de datos
        if st.session_state.get('df') is not None:
            st.markdown("---")
            st.subheader("📊 Resumen de Datos")
            
            df = st.session_state.df
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Registros", f"{len(df):,}")
            with col2:
                st.metric("Columnas", f"{len(df.columns)}")
            with col3:
                if 'fecha' in df.columns:
                    date_range = f"{df['fecha'].min().strftime('%Y-%m-%d')} a {df['fecha'].max().strftime('%Y-%m-%d')}"
                    st.metric("Período", date_range)
            with col4:
                if 'monto_venta' in df.columns:
                    st.metric("Ventas Totales", f"${df['monto_venta'].sum():,.0f}")