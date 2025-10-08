# src/modules/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

class DashboardModule:
    def __init__(self):
        self.name = "Dashboard"
        self.version = "1.0"
    
    def render(self):
        st.header("📊 Dashboard de Inteligencia Comercial")
        
        # Verificar si hay datos cargados
        if st.session_state.get('df') is None:
            st.warning("⚠️ No hay datos cargados. Ve a '🔗 Conectores' para cargar datos.")
            return
        
        df = st.session_state.df
        
        # Filtros globales
        col1, col2, col3 = st.columns(3)
        with col1:
            date_range = st.selectbox("Rango de Fechas:", ["Últimos 30 días", "Últimos 90 días", "Este año", "Todo"])
        with col2:
            if 'vendedor' in df.columns:
                sellers = ['Todos'] + list(df['vendedor'].unique())
                selected_seller = st.selectbox("Vendedor:", sellers)
        with col3:
            if 'region' in df.columns:
                regions = ['Todas'] + list(df['region'].unique())
                selected_region = st.selectbox("Región:", regions)
        
        # Aplicar filtros
        filtered_df = self._apply_filters(df, date_range, selected_seller, selected_region)
        
        # Métricas principales
        self._render_metrics(filtered_df)
        
        # Tabs de análisis
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Tendencia", "👥 Equipo", "📦 Productos", "🌍 Regional"])
        
        with tab1:
            self._render_trend_analysis(filtered_df)
        with tab2:
            self._render_team_analysis(filtered_df)
        with tab3:
            self._render_product_analysis(filtered_df)
        with tab4:
            self._render_regional_analysis(filtered_df)
    
    def _apply_filters(self, df, date_range, seller, region):
        """Aplicar filtros a los datos"""
        filtered_df = df.copy()
        
        # Filtrar por fecha
        if date_range == "Últimos 30 días":
            cutoff_date = datetime.now() - timedelta(days=30)
            filtered_df = filtered_df[filtered_df['fecha'] >= cutoff_date]
        elif date_range == "Últimos 90 días":
            cutoff_date = datetime.now() - timedelta(days=90)
            filtered_df = filtered_df[filtered_df['fecha'] >= cutoff_date]
        elif date_range == "Este año":
            current_year = datetime.now().year
            filtered_df = filtered_df[filtered_df['fecha'].dt.year == current_year]
        
        # Filtrar por vendedor
        if seller != 'Todos' and 'vendedor' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['vendedor'] == seller]
        
        # Filtrar por región
        if region != 'Todas' and 'region' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['region'] == region]
        
        return filtered_df
    
    def _render_metrics(self, df):
        """Renderizar métricas principales"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sales = df['monto_venta'].sum()
            st.metric("Ventas Totales", f"${total_sales:,.0f}")
        
        with col2:
            growth = self._calculate_growth(df)
            st.metric("Crecimiento", f"{growth:.1f}%")
        
        with col3:
            avg_sale = df['monto_venta'].mean()
            st.metric("Venta Promedio", f"${avg_sale:,.0f}")
        
        with col4:
            unique_customers = df['cliente'].nunique()
            st.metric("Clientes Únicos", f"{unique_customers}")
        
        # Segunda fila de métricas
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            if 'utilidad' in df.columns:
                total_profit = df['utilidad'].sum()
                st.metric("Utilidad Total", f"${total_profit:,.0f}")
        
        with col6:
            if 'utilidad' in df.columns:
                avg_margin = (df['utilidad'].sum() / df['monto_venta'].sum()) * 100
                st.metric("Margen Promedio", f"{avg_margin:.1f}%")
        
        with col7:
            transactions = len(df)
            st.metric("Transacciones", f"{transactions:,}")
        
        with col8:
            if 'vendedor' in df.columns:
                top_seller = df.groupby('vendedor')['monto_venta'].sum().idxmax()
                st.metric("Top Vendedor", top_seller)
    
    def _calculate_growth(self, df):
        """Calcular tasa de crecimiento"""
        if len(df) < 2:
            return 0.0
        
        try:
            monthly_sales = df.groupby(pd.Grouper(key='fecha', freq='M'))['monto_venta'].sum()
            if len(monthly_sales) > 1:
                return ((monthly_sales.iloc[-1] - monthly_sales.iloc[-2]) / monthly_sales.iloc[-2]) * 100
        except:
            pass
        return 0.0
    
    def _render_trend_analysis(self, df):
        """Análisis de tendencias"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Tendencia mensual
            monthly_trend = df.groupby(pd.Grouper(key='fecha', freq='M'))['monto_venta'].sum()
            fig_trend = px.line(
                monthly_trend.reset_index(),
                x='fecha',
                y='monto_venta',
                title='Tendencia de Ventas Mensuales',
                labels={'monto_venta': 'Ventas', 'fecha': 'Mes'}
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Estacionalidad semanal
            df['dia_semana'] = df['fecha'].dt.day_name()
            weekly_pattern = df.groupby('dia_semana')['monto_venta'].mean()
            fig_weekly = px.bar(
                weekly_pattern.reset_index(),
                x='dia_semana',
                y='monto_venta',
                title='Patrón Semanal de Ventas',
                labels={'monto_venta': 'Venta Promedio'}
            )
            st.plotly_chart(fig_weekly, use_container_width=True)
    
    def _render_team_analysis(self, df):
        """Análisis del equipo"""
        if 'vendedor' not in df.columns:
            st.info("ℹ️ No hay datos de vendedores para análisis de equipo")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance por vendedor
            seller_performance = df.groupby('vendedor').agg({
                'monto_venta': ['sum', 'count'],
                'cliente': 'nunique'
            }).round(2)
            
            seller_performance.columns = ['Ventas Totales', 'Transacciones', 'Clientes Únicos']
            seller_performance = seller_performance.sort_values('Ventas Totales', ascending=False)
            
            st.subheader("🏆 Performance por Vendedor")
            st.dataframe(seller_performance.style.format({
                'Ventas Totales': '${:,.0f}'
            }), use_container_width=True)
        
        with col2:
            # Gráfico de comparación
            top_sellers = df.groupby('vendedor')['monto_venta'].sum().nlargest(10)
            fig_sellers = px.bar(
                top_sellers.reset_index(),
                x='vendedor',
                y='monto_venta',
                title='Top 10 Vendedores',
                color='monto_venta'
            )
            st.plotly_chart(fig_sellers, use_container_width=True)
    
    def _render_product_analysis(self, df):
        """Análisis de productos"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Ventas por producto
            product_sales = df.groupby('producto_servicio')['monto_venta'].sum().sort_values(ascending=False)
            fig_products = px.pie(
                values=product_sales.values,
                names=product_sales.index,
                title='Distribución de Ventas por Producto'
            )
            st.plotly_chart(fig_products, use_container_width=True)
        
        with col2:
            # Rentabilidad por producto
            if 'utilidad' in df.columns:
                product_profit = df.groupby('producto_servicio')['utilidad'].sum().nlargest(10)
                fig_profit = px.bar(
                    product_profit.reset_index(),
                    x='producto_servicio',
                    y='utilidad',
                    title='Productos Más Rentables (Top 10)',
                    color='utilidad'
                )
                st.plotly_chart(fig_profit, use_container_width=True)
    
    def _render_regional_analysis(self, df):
        """Análisis regional"""
        if 'region' not in df.columns:
            st.info("ℹ️ No hay datos regionales para análisis geográfico")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Ventas por región
            region_sales = df.groupby('region')['monto_venta'].sum().sort_values(ascending=False)
            fig_region = px.bar(
                region_sales.reset_index(),
                x='region',
                y='monto_venta',
                title='Ventas por Región',
                color='monto_venta'
            )
            st.plotly_chart(fig_region, use_container_width=True)
        
        with col2:
            # Eficiencia regional
            region_metrics = df.groupby('region').agg({
                'monto_venta': ['sum', 'mean'],
                'cliente': 'nunique'
            }).round(2)
            
            region_metrics.columns = ['Ventas Totales', 'Venta Promedio', 'Clientes Únicos']
            st.subheader("📊 Métricas por Región")
            st.dataframe(region_metrics.style.format({
                'Ventas Totales': '${:,.0f}',
                'Venta Promedio': '${:,.0f}'
            }), use_container_width=True)