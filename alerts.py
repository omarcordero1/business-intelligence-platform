# src/modules/alerts.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class AlertsModule:
    def __init__(self):
        self.name = "Alerts"
        self.version = "1.0"
        self.active_alerts = []
        self.alert_history = []
    
    def render(self):
        st.header("🔔 Sistema de Alertas Inteligentes")
        st.markdown("Monitorea KPIs críticos y recibe notificaciones proactivas")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🚨 Alertas Activas", "⚙️ Configurar Alertas", "📊 Reglas de Negocio", "📋 Historial"])
        
        with tab1:
            self._render_active_alerts()
        with tab2:
            self._render_alert_configuration()
        with tab3:
            self._render_business_rules()
        with tab4:
            self._render_alert_history()
    
    def _render_active_alerts(self):
        """Mostrar alertas activas"""
        st.subheader("🚨 Alertas Activas")
        
        # Verificar datos y generar alertas
        if st.session_state.get('df') is not None:
            self._check_alerts(st.session_state.df)
        
        if not self.active_alerts:
            st.success("✅ No hay alertas activas - Todo está bajo control")
            return
        
        st.warning(f"⚠️ {len(self.active_alerts)} alertas requieren atención")
        
        for alert in self.active_alerts:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Color code por severidad
                    if alert['severity'] == 'high':
                        st.error(f"**🔴 {alert['title']}**")
                    elif alert['severity'] == 'medium':
                        st.warning(f"🟡 {alert['title']}")
                    else:
                        st.info(f"🔵 {alert['title']}")
                    
                    st.write(f"📅 {alert['timestamp']}")
                    st.write(f"📝 {alert['description']}")
                    
                    if 'metric_value' in alert:
                        st.write(f"📊 Valor actual: {alert['metric_value']}")
                    
                    if 'recommendation' in alert:
                        st.write(f"💡 **Recomendación:** {alert['recommendation']}")
                
                with col2:
                    if st.button("✅ Resolver", key=f"resolve_{alert['id']}"):
                        self._resolve_alert(alert['id'])
                        st.rerun()
                
                with col3:
                    if st.button("📋 Acción", key=f"action_{alert['id']}"):
                        self._take_action(alert)
                
                st.markdown("---")
    
    def _check_alerts(self, df):
        """Verificar y generar alertas basadas en datos"""
        self.active_alerts = []  # Reset alerts
        
        # Alertas de ventas
        self._check_sales_alerts(df)
        
        # Alertas de equipo
        if 'vendedor' in df.columns:
            self._check_team_alerts(df)
        
        # Alertas de productos
        self._check_product_alerts(df)
        
        # Alertas de clientes
        if 'cliente' in df.columns:
            self._check_customer_alerts(df)
    
    def _check_sales_alerts(self, df):
        """Verificar alertas de ventas"""
        # Alerta: Caída en ventas
        monthly_sales = df.groupby(pd.Grouper(key='fecha', freq='M'))['monto_venta'].sum()
        if len(monthly_sales) >= 2:
            current_month = monthly_sales.iloc[-1]
            previous_month = monthly_sales.iloc[-2]
            
            if current_month < previous_month * 0.8:  # 20% de caída
                self.active_alerts.append({
                    'id': 'sales_drop',
                    'title': 'Caída Significativa en Ventas',
                    'description': f'Ventas del mes actual (${current_month:,.0f}) son {((previous_month - current_month) / previous_month * 100):.1f}% menores que el mes anterior',
                    'severity': 'high',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'metric_value': f'${current_month:,.0f} vs ${previous_month:,.0f}',
                    'recommendation': 'Revisar estrategias comerciales y analizar causas de la caída'
                })
        
        # Alerta: Meta de ventas en riesgo
        total_sales = df['monto_venta'].sum()
        monthly_avg = total_sales / (df['fecha'].max() - df['fecha'].min()).days * 30
        if monthly_avg < 50000:  # Meta mensual de $50K
            self.active_alerts.append({
                'id': 'sales_target_risk',
                'title': 'Meta de Ventas en Riesgo',
                'description': f'Proyección mensual (${monthly_avg:,.0f}) está por debajo de la meta objetivo',
                'severity': 'medium',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'metric_value': f'Proyección: ${monthly_avg:,.0f}',
                'recommendation': 'Implementar acciones correctivas para alcanzar meta mensual'
            })
    
    def _check_team_alerts(self, df):
        """Verificar alertas del equipo"""
        seller_performance = df.groupby('vendedor')['monto_venta'].sum()
        avg_performance = seller_performance.mean()
        
        # Alerta: Vendedor con bajo performance
        underperformers = seller_performance[seller_performance < avg_performance * 0.6]
        for seller, sales in underperformers.items():
            self.active_alerts.append({
                'id': f'underperformer_{seller}',
                'title': f'Bajo Performance: {seller}',
                'description': f'Ventas de {seller} (${sales:,.0f}) están significativamente por debajo del promedio del equipo',
                'severity': 'medium',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'metric_value': f'${sales:,.0f} vs promedio ${avg_performance:,.0f}',
                'recommendation': f'Programar sesión de coaching con {seller} y revisar estrategias'
            })
        
        # Alerta: Distribución desigual de ventas
        gini_coefficient = self._calculate_gini(seller_performance)
        if gini_coefficient > 0.6:  # Alta desigualdad
            self.active_alerts.append({
                'id': 'uneven_distribution',
                'title': 'Distribución Desigual en Equipo',
                'description': 'Las ventas están muy concentradas en pocos vendedores',
                'severity': 'low',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'metric_value': f'Coeficiente Gini: {gini_coefficient:.2f}',
                'recommendation': 'Considerar redistribución de leads y programas de capacitación'
            })
    
    def _check_product_alerts(self, df):
        """Verificar alertas de productos"""
        product_sales = df.groupby('producto_servicio')['monto_venta'].sum()
        
        # Alerta: Producto con bajo desempeño
        total_sales = product_sales.sum()
        for product, sales in product_sales.items():
            if sales / total_sales < 0.02:  # Menos del 2% del total
                self.active_alerts.append({
                    'id': f'low_perf_product_{product}',
                    'title': f'Producto de Bajo Desempeño: {product}',
                    'description': f'El producto {product} representa solo el {(sales/total_sales*100):.1f}% de las ventas totales',
                    'severity': 'low',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'metric_value': f'${sales:,.0f} ({sales/total_sales*100:.1f}%)',
                    'recommendation': f'Evaluar estrategia de marketing para {product} o considerar discontinuación'
                })
    
    def _check_customer_alerts(self, df):
        """Verificar alertas de clientes"""
        customer_activity = df.groupby('cliente').agg({
            'fecha': ['max', 'count'],
            'monto_venta': 'sum'
        })
        
        customer_activity.columns = ['ultima_compra', 'frecuencia', 'total_comprado']
        max_date = df['fecha'].max()
        
        # Alerta: Clientes inactivos
        for customer, data in customer_activity.iterrows():
            days_since_last = (max_date - data['ultima_compra']).days
            if days_since_last > 90 and data['total_comprado'] > 10000:  # Cliente valioso inactivo
                self.active_alerts.append({
                    'id': f'inactive_customer_{customer}',
                    'title': f'Cliente Valioso Inactivo: {customer}',
                    'description': f'{customer} no ha realizado compras en {days_since_last} días',
                    'severity': 'medium',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'metric_value': f'Historial: ${data["total_comprado"]:,.0f}',
                    'recommendation': f'Contactar a {customer} con oferta especial de reactivación'
                })
    
    def _calculate_gini(self, values):
        """Calcular coeficiente Gini para desigualdad"""
        sorted_values = np.sort(values)
        n = len(sorted_values)
        index = np.arange(1, n + 1)
        return (np.sum((2 * index - n - 1) * sorted_values)) / (n * np.sum(sorted_values))
    
    def _resolve_alert(self, alert_id):
        """Resolver una alerta"""
        self.active_alerts = [alert for alert in self.active_alerts if alert['id'] != alert_id]
        
        # Agregar al historial
        resolved_alert = next((alert for alert in self.active_alerts if alert['id'] == alert_id), None)
        if resolved_alert:
            resolved_alert['resolved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.alert_history.append(resolved_alert)
    
    def _take_action(self, alert):
        """Tomar acción sobre una alerta"""
        st.info(f"🛠️ Ejecutando acción para: {alert['title']}")
        
        if 'sales_drop' in alert['id']:
            st.write("**Acciones recomendadas:**")
            st.write("1. Revisar pipeline de ventas actual")
            st.write("2. Analizar causas de la caída")
            st.write("3. Implementar campaña de recuperación")
            st.write("4. Programar reunión de emergencia con equipo")
        
        elif 'underperformer' in alert['id']:
            st.write("**Acciones recomendadas:**")
            st.write("1. Programar sesión one-on-one")
            st.write("2. Revisar técnicas de venta")
            st.write("3. Asignar mentor del equipo")
            st.write("4. Establecer metas progresivas")
        
        elif 'inactive_customer' in alert['id']:
            st.write("**Acciones recomendadas:**")
            st.write("1. Llamada personalizada de seguimiento")
            st.write("2. Oferta especial de reactivación")
            st.write("3. Invitación a evento exclusivo")
            st.write("4. Programa de lealtad personalizado")
    
    def _render_alert_configuration(self):
        """Configuración de alertas"""
        st.subheader("⚙️ Configurar Alertas Personalizadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Alertas de Ventas**")
            
            with st.form("sales_alerts"):
                st.write("Configurar umbrales de ventas")
                
                sales_drop_threshold = st.slider(
                    "Umbral caída ventas (%):",
                    min_value=5, max_value=50, value=20
                )
                
                sales_target = st.number_input(
                    "Meta mensual de ventas:",
                    min_value=1000, value=50000, step=1000
                )
                
                enable_daily_alerts = st.checkbox("Alertas diarias de performance", value=True)
                
                if st.form_submit_button("💾 Guardar Configuración"):
                    st.success("✅ Configuración de alertas de ventas guardada")
        
        with col2:
            st.write("**👥 Alertas de Equipo**")
            
            with st.form("team_alerts"):
                st.write("Configurar monitoreo de equipo")
                
                performance_threshold = st.slider(
                    "Umbral bajo performance (% del promedio):",
                    min_value=10, max_value=80, value=60
                )
                
                enable_coaching_alerts = st.checkbox("Alertas para sesiones de coaching", value=True)
                enable_achievement_alerts = st.checkbox("Alertas de logros", value=True)
                
                if st.form_submit_button("💾 Guardar Configuración"):
                    st.success("✅ Configuración de alertas de equipo guardada")
        
        st.write("**🔔 Métodos de Notificación**")
        col_notif1, col_notif2, col_notif3 = st.columns(3)
        
        with col_notif1:
            email_notifications = st.checkbox("📧 Email", value=True)
            email_address = st.text_input("Email para notificaciones:")
        
        with col_notif2:
            slack_notifications = st.checkbox("💬 Slack", value=False)
            slack_channel = st.text_input("Canal de Slack:")
        
        with col_notif3:
            sms_notifications = st.checkbox("📱 SMS", value=False)
            phone_number = st.text_input("Número para SMS:")
        
        if st.button("💾 Guardar Preferencias de Notificación"):
            st.success("✅ Preferencias de notificación guardadas")
    
    def _render_business_rules(self):
        """Reglas de negocio para alertas"""
        st.subheader("📊 Reglas de Negocio para Alertas")
        
        st.info("Define reglas personalizadas para generar alertas automáticas")
        
        # Reglas predefinidas
        rules = [
            {
                "name": "Caída de Ventas Crítica",
                "description": "Ventas caen más del 30% respecto al mes anterior",
                "active": True,
                "severity": "high"
            },
            {
                "name": "Cliente Valioso Inactivo", 
                "description": "Cliente que gastó >$10K no compra en 90 días",
                "active": True,
                "severity": "medium"
            },
            {
                "name": "Bajo Performance de Equipo",
                "description": "Vendedor con ventas <60% del promedio del equipo", 
                "active": True,
                "severity": "medium"
            },
            {
                "name": "Producto de Bajo Desempeño",
                "description": "Producto con menos del 2% de participación en ventas",
                "active": False,
                "severity": "low"
            }
        ]
        
        for i, rule in enumerate(rules):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{rule['name']}**")
                st.write(rule['description'])
                st.write(f"Severidad: {rule['severity'].upper()}")
            
            with col2:
                new_status = st.checkbox("Activo", value=rule['active'], key=f"rule_{i}")
                if new_status != rule['active']:
                    rule['active'] = new_status
            
            with col3:
                if st.button("✏️ Editar", key=f"edit_{i}"):
                    st.info(f"Editando regla: {rule['name']}")
        
        # Crear nueva regla
        st.markdown("---")
        st.write("**➕ Crear Nueva Regla**")
        
        with st.form("new_rule"):
            col1, col2 = st.columns(2)
            
            with col1:
                rule_name = st.text_input("Nombre de la regla:")
                rule_description = st.text_area("Descripción:")
            
            with col2:
                rule_metric = st.selectbox("Métrica a monitorear:", 
                                         ["Ventas", "Clientes activos", "Performance equipo", "Margen utilidad"])
                rule_condition = st.selectbox("Condición:", ["Menor que", "Mayor que", "Igual a", "Diferente de"])
                rule_value = st.number_input("Valor umbral:")
                rule_severity = st.selectbox("Severidad:", ["low", "medium", "high"])
            
            if st.form_submit_button("➕ Agregar Regla"):
                st.success("✅ Nueva regla agregada")
    
    def _render_alert_history(self):
        """Historial de alertas"""
        st.subheader("📋 Historial de Alertas")
        
        if not self.alert_history:
            st.info("ℹ️ No hay historial de alertas resueltas")
            return
        
        # Filtrar por fecha
        date_filter = st.selectbox("Filtrar por:", ["Últimos 7 días", "Últimos 30 días", "Últimos 90 días", "Todo"])
        
        filtered_history = self._filter_history_by_date(date_filter)
        
        st.write(f"**📊 {len(filtered_history)} alertas resueltas**")
        
        for alert in filtered_history:
            with st.expander(f"✅ {alert['title']} - {alert.get('resolved_at', 'N/A')}"):
                st.write(f"**Descripción:** {alert['description']}")
                st.write(f"**Severidad:** {alert['severity']}")
                st.write(f"**Creada:** {alert['timestamp']}")
                st.write(f"**Resuelta:** {alert.get('resolved_at', 'N/A')}")
                
                if 'metric_value' in alert:
                    st.write(f"**Métrica:** {alert['metric_value']}")
                
                if 'recommendation' in alert:
                    st.write(f"**Recomendación aplicada:** {alert['recommendation']}")
    
    def _filter_history_by_date(self, date_filter):
        """Filtrar historial por fecha"""
        if date_filter == "Últimos 7 días":
            cutoff = datetime.now() - timedelta(days=7)
        elif date_filter == "Últimos 30 días":
            cutoff = datetime.now() - timedelta(days=30)
        elif date_filter == "Últimos 90 días":
            cutoff = datetime.now() - timedelta(days=90)
        else:
            return self.alert_history
        
        # Convertir timestamps a datetime para filtrado
        filtered = []
        for alert in self.alert_history:
            if 'resolved_at' in alert:
                resolved_date = datetime.strptime(alert['resolved_at'], '%Y-%m-%d %H:%M')
                if resolved_date >= cutoff:
                    filtered.append(alert)
        
        return filtered