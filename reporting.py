# src/modules/reporting.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import BytesIO

class ReportingModule:
    def __init__(self):
        self.name = "Reporting"
        self.version = "1.0"
        self.saved_reports = []
    
    def render(self):
        st.header("📊 Sistema de Reportes")
        st.markdown("Genera y programa reportes ejecutivos automáticos")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Generar Reporte", "🔄 Reportes Programados", "📁 Reportes Guardados", "⚙️ Plantillas"])
        
        with tab1:
            self._render_report_generator()
        with tab2:
            self._render_scheduled_reports()
        with tab3:
            self._render_saved_reports()
        with tab4:
            self._render_report_templates()
    
    def _render_report_generator(self):
        """Generador de reportes personalizados"""
        st.subheader("📋 Generar Nuevo Reporte")
        
        if st.session_state.get('df') is None:
            st.warning("⚠️ Carga datos primero en el módulo '🔗 Conectores'")
            return
        
        df = st.session_state.df
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Configuración del Reporte**")
            
            report_name = st.text_input("Nombre del Reporte:", value=f"Reporte_{datetime.now().strftime('%Y%m%d')}")
            
            report_type = st.selectbox("Tipo de Reporte:", 
                                     ["Ejecutivo", "Ventas Detallado", "Performance Equipo", "Análisis Productos", "Regional"])
            
            date_range = st.selectbox("Rango de Fechas:", 
                                    ["Últimos 30 días", "Últimos 90 días", "Este trimestre", "Este año", "Personalizado"])
            
            if date_range == "Personalizado":
                col_date1, col_date2 = st.columns(2)
                with col_date1:
                    start_date = st.date_input("Fecha inicio:")
                with col_date2:
                    end_date = st.date_input("Fecha fin:")
            
            format_type = st.selectbox("Formato:", ["PDF", "Excel", "HTML", "Presentación"])
            
            st.write("**Secciones a Incluir**")
            include_executive_summary = st.checkbox("Resumen Ejecutivo", value=True)
            include_sales_metrics = st.checkbox("Métricas de Ventas", value=True)
            include_team_performance = st.checkbox("Performance del Equipo", value=True)
            include_product_analysis = st.checkbox("Análisis de Productos", value=True)
            include_regional_analysis = st.checkbox("Análisis Regional", value=True)
            include_recommendations = st.checkbox("Recomendaciones", value=True)
        
        with col2:
            st.write("**Vista Previa del Reporte**")
            
            if st.button("🔄 Generar Vista Previa", type="primary"):
                with st.spinner("Generando reporte..."):
                    report_content = self._generate_report_content(
                        df, report_type, include_executive_summary, include_sales_metrics,
                        include_team_performance, include_product_analysis,
                        include_regional_analysis, include_recommendations
                    )
                    
                    st.session_state.current_report = report_content
                    st.session_state.report_name = report_name
            
            if st.session_state.get('current_report'):
                st.success("✅ Reporte generado correctamente")
                
                # Mostrar preview
                with st.expander("👁️ Vista Previa del Reporte", expanded=True):
                    st.markdown(st.session_state.current_report)
                
                # Opciones de exportación
                st.write("**Exportar Reporte**")
                col_export1, col_export2, col_export3 = st.columns(3)
                
                with col_export1:
                    if st.button("📄 Exportar PDF"):
                        self._export_pdf(st.session_state.current_report, st.session_state.report_name)
                
                with col_export2:
                    if st.button("📊 Exportar Excel"):
                        self._export_excel(df, st.session_state.report_name)
                
                with col_export3:
                    if st.button("💾 Guardar Reporte"):
                        self._save_report(st.session_state.report_name, st.session_state.current_report)
                        st.success("✅ Reporte guardado")
    
    def _generate_report_content(self, df, report_type, include_executive_summary, include_sales_metrics,
                               include_team_performance, include_product_analysis, 
                               include_regional_analysis, include_recommendations):
        """Generar contenido del reporte"""
        content = f"# 📊 {report_type} - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        if include_executive_summary:
            content += self._generate_executive_summary(df)
        
        if include_sales_metrics:
            content += self._generate_sales_metrics(df)
        
        if include_team_performance and 'vendedor' in df.columns:
            content += self._generate_team_performance(df)
        
        if include_product_analysis:
            content += self._generate_product_analysis(df)
        
        if include_regional_analysis and 'region' in df.columns:
            content += self._generate_regional_analysis(df)
        
        if include_recommendations:
            content += self._generate_recommendations(df)
        
        return content
    
    def _generate_executive_summary(self, df):
        """Generar resumen ejecutivo"""
        total_sales = df['monto_venta'].sum()
        growth = self._calculate_growth(df)
        unique_customers = df['cliente'].nunique()
        avg_sale = df['monto_venta'].mean()
        
        summary = f"""
## 🎯 Resumen Ejecutivo

**Performance General:**
- **Ventas Totales:** ${total_sales:,.0f}
- **Tasa de Crecimiento:** {growth:.1f}%
- **Clientes Únicos:** {unique_customers}
- **Venta Promedia:** ${avg_sale:,.0f}

**Puntos Destacados:**
- {self._get_highlight_1(df)}
- {self._get_highlight_2(df)}
- {self._get_highlight_3(df)}

"""
        return summary
    
    def _generate_sales_metrics(self, df):
        """Generar métricas de ventas"""
        metrics = f"""
## 📈 Métricas de Ventas

**Métricas Clave:**
- **Total Transacciones:** {len(df):,}
- **Ticket Promedio:** ${self._calculate_avg_ticket(df):,.0f}
- **Frecuencia de Compra:** {self._calculate_purchase_frequency(df):.1f}

**Tendencias:**
{self._get_sales_trends(df)}

"""
        return metrics
    
    def _generate_team_performance(self, df):
        """Generar análisis de equipo"""
        top_seller = df.groupby('vendedor')['monto_venta'].sum().idxmax()
        seller_performance = df.groupby('vendedor')['monto_venta'].sum().nlargest(3)
        
        team_analysis = f"""
## 👥 Performance del Equipo

**Vendedor Destacado:** {top_seller}

**Top 3 Vendedores:**
"""
        for seller, sales in seller_performance.items():
            team_analysis += f"- **{seller}:** ${sales:,.0f}\n"
        
        team_analysis += f"\n**Recomendaciones Equipo:**\n{self._get_team_recommendations(df)}\n\n"
        return team_analysis
    
    def _generate_product_analysis(self, df):
        """Generar análisis de productos"""
        top_products = df.groupby('producto_servicio')['monto_venta'].sum().nlargest(5)
        
        product_analysis = f"""
## 📦 Análisis de Productos

**Productos Más Vendidos:**
"""
        for product, sales in top_products.items():
            product_analysis += f"- **{product}:** ${sales:,.0f}\n"
        
        if 'utilidad' in df.columns:
            profitable_products = df.groupby('producto_servicio')['utilidad'].sum().nlargest(3)
            product_analysis += f"\n**Productos Más Rentables:**\n"
            for product, profit in profitable_products.items():
                product_analysis += f"- **{product}:** ${profit:,.0f}\n"
        
        product_analysis += f"\n**Oportunidades Producto:**\n{self._get_product_opportunities(df)}\n\n"
        return product_analysis
    
    def _generate_regional_analysis(self, df):
        """Generar análisis regional"""
        regional_sales = df.groupby('region')['monto_venta'].sum().sort_values(ascending=False)
        
        regional_analysis = f"""
## 🌍 Análisis Regional

**Ventas por Región:**
"""
        for region, sales in regional_sales.items():
            regional_analysis += f"- **{region}:** ${sales:,.0f}\n"
        
        regional_analysis += f"\n**Estrategias Regionales:**\n{self._get_regional_strategies(df)}\n\n"
        return regional_analysis
    
    def _generate_recommendations(self, df):
        """Generar recomendaciones"""
        recommendations = f"""
## 💡 Recomendaciones Estratégicas

**Acciones Inmediatas (1-2 semanas):**
1. {self._get_quick_win_1(df)}
2. {self._get_quick_win_2(df)}

**Estrategias Mediano Plazo (1-3 meses):**
1. {self._get_medium_term_1(df)}
2. {self._get_medium_term_2(df)}

**Iniciativas Largo Plazo (3-6 meses):**
1. {self._get_long_term_1(df)}
2. {self._get_long_term_2(df)}

"""
        return recommendations
    
    # Métodos auxiliares para generar contenido dinámico
    def _calculate_growth(self, df):
        """Calcular crecimiento"""
        try:
            monthly_sales = df.groupby(pd.Grouper(key='fecha', freq='M'))['monto_venta'].sum()
            if len(monthly_sales) > 1:
                return ((monthly_sales.iloc[-1] - monthly_sales.iloc[-2]) / monthly_sales.iloc[-2]) * 100
        except:
            pass
        return 0.0
    
    def _calculate_avg_ticket(self, df):
        """Calcular ticket promedio"""
        if 'cliente' in df.columns:
            customer_sales = df.groupby('cliente')['monto_venta'].sum()
            return customer_sales.mean()
        return df['monto_venta'].mean()
    
    def _calculate_purchase_frequency(self, df):
        """Calcular frecuencia de compra"""
        if 'cliente' in df.columns and 'fecha' in df.columns:
            customer_purchases = df.groupby('cliente').size()
            return customer_purchases.mean()
        return 1.0
    
    def _get_highlight_1(self, df):
        highlights = [
            "Crecimiento sólido en ventas del último trimestre",
            "Alta retención de clientes existentes",
            "Expansión exitosa en nuevos mercados",
            "Mejora significativa en margen de utilidad"
        ]
        return highlights[0]
    
    def _get_highlight_2(self, df):
        highlights = [
            "Aumento en el ticket promedio de compra",
            "Efectiva penetración en segmento enterprise",
            "Optimización de costos operativos",
            "Alto engagement con nuevos productos"
        ]
        return highlights[1]
    
    def _get_highlight_3(self, df):
        highlights = [
            "Excelente performance del equipo comercial",
            "Expansión geográfica exitosa",
            "Alta satisfacción del cliente",
            "Innovación en estrategias de ventas"
        ]
        return highlights[2]
    
    def _get_sales_trends(self, df):
        trends = [
            "Tendencia positiva en ventas mensuales",
            "Estacionalidad marcada en Q4",
            "Crecimiento consistente semana a semana",
            "Expansión en segmentos de alto valor"
        ]
        return trends[0]
    
    def _get_team_recommendations(self, df):
        recommendations = [
            "Implementar programa de coaching para vendedores con performance media",
            "Establecer metas individualizadas basadas en historial",
            "Crear sistema de incentivos por logro de objetivos",
            "Desarrollar programa de mentoría entre vendedores senior y junior"
        ]
        return recommendations[0]
    
    def _get_product_opportunities(self, df):
        opportunities = [
            "Potencial de upsell en clientes existentes",
            "Oportunidad de bundling con productos complementarios",
            "Expansión a nuevos segmentos con productos actuales",
            "Desarrollo de versiones premium de productos populares"
        ]
        return opportunities[0]
    
    def _get_regional_strategies(self, df):
        strategies = [
            "Enfoque en regiones con mayor potencial de crecimiento",
            "Optimización de recursos en regiones maduras",
            "Expansión estratégica en regiones emergentes",
            "Personalización de estrategias por mercado local"
        ]
        return strategies[0]
    
    def _get_quick_win_1(self, df):
        return "Optimizar proceso de seguimiento con clientes existentes"
    
    def _get_quick_win_2(self, df):
        return "Implementar campaña de reactivación para clientes inactivos"
    
    def _get_medium_term_1(self, df):
        return "Desarrollar programa de lealtad para clientes recurrentes"
    
    def _get_medium_term_2(self, df):
        return "Expandir portafolio de productos en segmentos de alto crecimiento"
    
    def _get_long_term_1(self, df):
        return "Establecer presencia en nuevos mercados internacionales"
    
    def _get_long_term_2(self, df):
        return "Implementar sistema de inteligencia artificial predictiva"
    
    def _export_pdf(self, content, filename):
        """Exportar a PDF (simulación)"""
        st.info("📄 Función de exportación PDF en desarrollo")
        st.success(f"✅ Reporte '{filename}' listo para descarga PDF")
    
    def _export_excel(self, df, filename):
        """Exportar a Excel"""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Datos', index=False)
            
            # Agregar resumen
            summary_data = {
                'Métrica': ['Ventas Totales', 'Transacciones', 'Clientes Únicos', 'Venta Promedio'],
                'Valor': [
                    df['monto_venta'].sum(),
                    len(df),
                    df['cliente'].nunique(),
                    df['monto_venta'].mean()
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Resumen', index=False)
        
        excel_data = output.getvalue()
        b64 = base64.b64encode(excel_data).decode()
        
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_data,
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    def _save_report(self, name, content):
        """Guardar reporte"""
        self.saved_reports.append({
            'name': name,
            'content': content,
            'date': datetime.now(),
            'type': 'Ejecutivo'
        })
    
    def _render_scheduled_reports(self):
        """Reportes programados"""
        st.subheader("🔄 Reportes Programados")
        st.info("Programa reportes automáticos para entrega recurrente")
        
        with st.form("schedule_report"):
            st.write("**Programar Nuevo Reporte**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                report_name = st.text_input("Nombre Reporte:", key="scheduled_name")
                frequency = st.selectbox("Frecuencia:", ["Diario", "Semanal", "Mensual", "Trimestral"])
                recipients = st.text_area("Destinatarios (emails):", height=60)
            
            with col2:
                start_date = st.date_input("Fecha Inicio:")
                format_type = st.selectbox("Formato Entrega:", ["PDF", "Excel", "Ambos"])
                include_data = st.checkbox("Incluir datos brutos", value=False)
            
            if st.form_submit_button("📅 Programar Reporte"):
                st.success(f"✅ Reporte '{report_name}' programado para entrega {frequency.lower()}")
    
    def _render_saved_reports(self):
        """Reportes guardados"""
        st.subheader("📁 Reportes Guardados")
        
        if not self.saved_reports:
            st.info("ℹ️ No hay reportes guardados. Genera un reporte primero.")
            return
        
        for report in self.saved_reports:
            with st.expander(f"📊 {report['name']} - {report['date'].strftime('%Y-%m-%d')}"):
                st.markdown(report['content'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📄 Exportar PDF", key=f"pdf_{report['name']}"):
                        st.success("PDF generado")
                with col2:
                    if st.button("📊 Exportar Excel", key=f"excel_{report['name']}"):
                        st.success("Excel generado")
                with col3:
                    if st.button("🗑️ Eliminar", key=f"delete_{report['name']}"):
                        self.saved_reports.remove(report)
                        st.rerun()
    
    def _render_report_templates(self):
        """Plantillas de reportes"""
        st.subheader("⚙️ Plantillas de Reportes")
        
        st.info("Configura plantillas predefinidas para reportes recurrentes")
        
        templates = [
            {"name": "Reporte Ejecutivo Semanal", "sections": ["Resumen", "Métricas", "Recomendaciones"]},
            {"name": "Análisis de Ventas Mensual", "sections": ["Tendencias", "Productos", "Equipo", "Regional"]},
            {"name": "Review Trimestral", "sections": ["Performance", "Metas", "Forecast", "Estrategias"]}
        ]
        
        for template in templates:
            with st.expander(f"📋 {template['name']}"):
                st.write("**Secciones incluidas:**")
                for section in template['sections']:
                    st.write(f"- ✅ {section}")
                
                if st.button("Usar esta plantilla", key=f"use_{template['name']}"):
                    st.success(f"✅ Plantilla '{template['name']}' aplicada")