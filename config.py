# src/utils/config.py
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración centralizada de la aplicación"""
    
    # Configuración de la aplicación
    APP_NAME = "Business Intelligence Platform"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Plataforma unificada de inteligencia comercial"
    
    # Configuración de API Keys (con fallback a secrets de Streamlit)
    @staticmethod
    def get_openai_key():
        """Obtener API key de OpenAI de forma segura"""
        try:
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                return st.secrets['OPENAI_API_KEY']
        except:
            pass
        
        return os.getenv('OPENAI_API_KEY', '')
    
    @staticmethod
    def get_database_url():
        """Obtener URL de base de datos"""
        try:
            if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
                return st.secrets['DATABASE_URL']
        except:
            pass
        
        return os.getenv('DATABASE_URL', 'sqlite:///bi_platform.db')
    
    # Configuración de módulos
    MODULES_CONFIG = {
        'dashboard': {
            'enabled': True,
            'name': 'Dashboard',
            'description': 'Dashboard unificado de métricas'
        },
        'sales_copilot': {
            'enabled': True,
            'name': 'Sales Copilot',
            'description': 'Asistente IA para ventas'
        },
        'data_connectors': {
            'enabled': True,
            'name': 'Data Connectors',
            'description': 'Conectores de datos'
        },
        'reporting': {
            'enabled': True,
            'name': 'Reporting',
            'description': 'Sistema de reportes'
        },
        'alerts': {
            'enabled': True,
            'name': 'Alerts',
            'description': 'Sistema de alertas'
        }
    }
    
    # Configuración de UI
    UI_CONFIG = {
        'theme': {
            'primary_color': '#667eea',
            'secondary_color': '#764ba2',
            'background_color': '#f8f9fa',
            'text_color': '#333333'
        },
        'layout': {
            'sidebar_width': 'wide',
            'main_width': 'wide',
            'default_view': 'dashboard'
        }
    }
    
    # Configuración de datos
    DATA_CONFIG = {
        'supported_formats': ['csv', 'xlsx', 'xls', 'json'],
        'max_file_size': 100,  # MB
        'auto_clean': True,
        'backup_enabled': True
    }