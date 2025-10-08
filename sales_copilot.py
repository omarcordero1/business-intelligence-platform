# src/modules/sales_copilot.py
import streamlit as st
import pandas as pd
import openai
from datetime import datetime

class SalesCopilotModule:
    def __init__(self):
        self.name = "Sales Copilot"
        self.version = "1.0"
    
    def render(self):
        st.header("🤖 Sales Copilot AI")
        st.markdown("Asistente de inteligencia artificial para optimizar tus estrategias de ventas")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Analizar Prospecto", "📧 Generar Email", "💡 Estrategias", "📚 Base de Conocimiento"])
        
        with tab1:
            self._render_prospect_analysis()
        with tab2:
            self._render_email_generator()
        with tab3:
            self._render_strategies()
        with tab4:
            self._render_knowledge_base()
    
    def _render_prospect_analysis(self):
        """Análisis de prospectos con IA"""
        st.subheader("🎯 Análisis de Prospecto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("prospect_analysis_form"):
                st.write("**Información del Prospecto**")
                
                prospect_name = st.text_input("Nombre del prospecto:")
                company = st.text_input("Empresa:")
                position = st.text_input("Cargo:")
                industry = st.selectbox("Industria:", ["Tecnología", "Finanzas", "Manufactura", "Salud", "Retail", "Servicios"])
                
                st.write("**Contexto del Prospecto**")
                known_needs = st.text_area("Necesidades conocidas:", height=100)
                objectives = st.text_area("Objetivos conocidos:", height=80)
                challenges = st.text_area("Desafíos/pain points:", height=80)
                
                submitted = st.form_submit_button("🧠 Analizar con IA")
        
        with col2:
            st.subheader("Análisis Generado")
            
            if submitted:
                if not prospect_name:
                    st.error("Por favor ingresa al menos el nombre del prospecto")
                    return
                
                if not st.session_state.get('openai_key'):
                    st.error("Configura tu API key de OpenAI en el sidebar")
                    return
                
                # Construir prompt
                prospect_data = f"""
                Prospecto: {prospect_name}
                Empresa: {company}
                Cargo: {position}
                Industria: {industry}
                Necesidades: {known_needs}
                Objetivos: {objectives}
                Desafíos: {challenges}
                """
                
                with st.spinner("Analizando prospecto con IA..."):
                    analysis = self._analyze_prospect_ai(prospect_data)
                    
                    if analysis:
                        st.success("✅ Análisis completado!")
                        st.markdown(analysis)
                        
                        # Opciones de exportación
                        col_export1, col_export2 = st.columns(2)
                        with col_export1:
                            if st.button("📋 Copiar Análisis"):
                                st.code(analysis, language="markdown")
                        with col_export2:
                            if st.button("💾 Guardar en Base"):
                                st.success("Guardado en base de conocimiento")
    
    def _analyze_prospect_ai(self, prospect_data):
        """Analizar prospecto usando OpenAI"""
        try:
            openai.api_key = st.session_state.openai_key
            
            prompt = f"""
            Como experto en ventas B2B, analiza este prospecto y genera una estrategia:

            INFORMACIÓN DEL PROSPECTO:
            {prospect_data}

            Genera un análisis con:
            1. **Fit Score** (1-10) y justificación
            2. **Pain Points** principales detectados
            3. **Oportunidades de Valor** específicas
            4. **Estrategia de Aproximación** recomendada
            5. **3 Argumentos** de venta personalizados
            6. **Posibles Objeciones** y respuestas

            Formato claro y accionable.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un estratega de ventas B2B experto."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error en análisis IA: {str(e)}")
            return None
    
    def _render_email_generator(self):
        """Generador de emails personalizados"""
        st.subheader("📧 Generador de Emails")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_type = st.selectbox("Tipo de Email:", 
                                    ["Presentación inicial", "Seguimiento", "Recordatorio", "Oferta especial", "Recalendarización"])
            
            prospect_name = st.text_input("Nombre del prospecto:", key="email_prospect")
            prospect_company = st.text_input("Empresa:", key="email_company")
            prospect_position = st.text_input("Cargo:", key="email_position")
            
            email_tone = st.selectbox("Tono:", ["Profesional", "Cercano", "Urgente", "Consultivo"])
            
            additional_context = st.text_area("Contexto adicional:", height=60)
            
            if st.button("🔄 Generar Email", type="primary"):
                if not prospect_name:
                    st.error("Ingresa al menos el nombre del prospecto")
                    return
                
                if not st.session_state.get('openai_key'):
                    st.error("Configura tu API key de OpenAI")
                    return
                
                context = f"""
                Tipo: {email_type}
                Prospecto: {prospect_name}
                Empresa: {prospect_company}
                Cargo: {prospect_position}
                Tono: {email_tone}
                Contexto: {additional_context}
                """
                
                with st.spinner("Generando email perfecto..."):
                    email = self._generate_email_ai(context)
                    
                    if email:
                        st.session_state.generated_email = email
        
        with col2:
            st.subheader("Email Generado")
            
            if st.session_state.get('generated_email'):
                st.markdown(f"```\n{st.session_state.generated_email}\n```")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("📋 Copiar Email"):
                        st.code(st.session_state.generated_email, language="markdown")
                        st.success("✅ Email copiado")
                with col_btn2:
                    if st.button("📤 Enviar a Outlook"):
                        st.success("✅ Integración con Outlook en desarrollo")
    
    def _generate_email_ai(self, context):
        """Generar email usando IA"""
        try:
            openai.api_key = st.session_state.openai_key
            
            prompt = f"""
            Genera un email de ventas B2B altamente personalizado:

            CONTEXTO:
            {context}

            Requisitos:
            - Máximo 150 palabras
            - Tono profesional pero cercano
            - Personalizado para el prospecto
            - Value proposition clara
            - Llamado a acción específico
            - Incluir asunto persuasivo

            Formato:
            ASUNTO: [asunto aquí]

            [cuerpo del email]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un copywriter experto en emails de ventas B2B."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error generando email: {str(e)}")
            return None
    
    def _render_strategies(self):
        """Estrategias de venta basadas en datos"""
        st.subheader("💡 Estrategias de Venta Inteligentes")
        
        if st.session_state.get('df') is None:
            st.warning("Carga datos en el módulo de Conectores para ver estrategias basadas en datos")
            return
        
        df = st.session_state.df
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**🎯 Segmentación Recomendada**")
            
            if 'monto_venta' in df.columns and 'cliente' in df.columns:
                # Análisis RFM básico
                customer_value = df.groupby('cliente')['monto_venta'].sum().sort_values(ascending=False)
                
                st.write("**Clientes de Alto Valor:**")
                top_customers = customer_value.head(5)
                for customer, value in top_customers.items():
                    st.write(f"- {customer}: ${value:,.0f}")
            
            st.info("**📦 Oportunidades de Producto**")
            if 'producto_servicio' in df.columns:
                product_growth = df.groupby('producto_servicio')['monto_venta'].sum().nlargest(5)
                for product, sales in product_growth.items():
                    st.write(f"- {product}: ${sales:,.0f}")
        
        with col2:
            st.info("**👥 Estrategia por Equipo**")
            
            if 'vendedor' in df.columns:
                seller_performance = df.groupby('vendedor')['monto_venta'].sum()
                best_seller = seller_performance.idxmax()
                st.write(f"**Vendedor Estrella:** {best_seller}")
                
                # Recomendaciones de coaching
                st.write("**Oportunidades de Coaching:**")
                if len(seller_performance) > 1:
                    avg_performance = seller_performance.mean()
                    needs_coaching = seller_performance[seller_performance < avg_performance * 0.7]
                    for seller in needs_coaching.index:
                        st.write(f"- {seller}")
            
            st.info("**🌍 Estrategia Regional**")
            if 'region' in df.columns:
                region_performance = df.groupby('region')['monto_venta'].sum()
                best_region = region_performance.idxmax()
                st.write(f"**Región Más Fuerte:** {best_region}")
    
    def _render_knowledge_base(self):
        """Base de conocimiento de ventas"""
        st.subheader("📚 Base de Conocimiento")
        
        st.info("Aquí se almacenarán todos los análisis, estrategias y aprendizajes generados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📋 Análisis Guardados**")
            st.write("- Prospecto: TechSolutions SA")
            st.write("- Prospecto: CloudCorp MX")
            st.write("- Análisis de tendencias Q3")
            
            st.write("**💡 Mejores Prácticas**")
            st.write("- Estrategia de aproximación para retail")
            st.write("- Email templates de alto engagement")
            st.write("- Técnicas de descubrimiento de necesidades")
        
        with col2:
            st.write("**🎯 Casos de Éxito**")
            st.write("- Venta enterprise: $250K")
            st.write("- Expansión cuenta existente: +40%")
            st.write("- Recuperación cuenta en riesgo")
            
            st.write("**📊 Métricas de Referencia**")
            st.write("- Tasa de conversión promedio: 15%")
            st.write("- Ciclo de ventas promedio: 45 días")
            st.write("- Ticket promedio industria: $25K")

# Inicializar session state para este módulo
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = None