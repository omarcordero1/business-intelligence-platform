# src/utils/helpers.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class DataHelpers:
    """Helper functions para procesamiento de datos"""
    
    @staticmethod
    def standardize_dataframe(df):
        """Estandarizar DataFrame a formato común"""
        df_standardized = df.copy()
        
        # Mapeo de columnas
        column_mapping = {
            'fecha': ['fecha', 'date', 'fecha_venta', 'timestamp', 'Date'],
            'cliente': ['cliente', 'client', 'customer', 'empresa', 'Customer'],
            'producto_servicio': ['producto_servicio', 'producto', 'servicio', 'product', 'service', 'Product'],
            'monto_venta': ['monto_venta', 'venta', 'monto', 'sales', 'amount', 'valor', 'Amount'],
            'vendedor': ['vendedor', 'seller', 'sales_rep', 'ejecutivo', 'SalesRep'],
            'region': ['region', 'zona', 'territory', 'area', 'Region'],
            'costo': ['costo', 'cost', 'costo_venta', 'Cost'],
            'comision': ['comision', 'commission', 'Commission']
        }
        
        # Renombrar columnas
        for standard_name, alternatives in column_mapping.items():
            for alt_name in alternatives:
                if alt_name in df_standardized.columns and standard_name not in df_standardized.columns:
                    df_standardized[standard_name] = df_standardized[alt_name]
                    break
        
        # Limpieza de datos
        df_standardized = DataHelpers.clean_dataframe(df_standardized)
        
        return df_standardized
    
    @staticmethod
    def clean_dataframe(df):
        """Limpiar y validar DataFrame"""
        df_clean = df.copy()
        
        # Convertir fecha
        if 'fecha' in df_clean.columns:
            df_clean['fecha'] = pd.to_datetime(df_clean['fecha'], errors='coerce')
        
        # Validar monto_venta
        if 'monto_venta' in df_clean.columns:
            df_clean['monto_venta'] = pd.to_numeric(df_clean['monto_venta'], errors='coerce')
            # Remover valores negativos o cero
            df_clean = df_clean[df_clean['monto_venta'] > 0]
        
        # Remover filas con datos críticos faltantes
        critical_columns = ['fecha', 'cliente', 'monto_venta']
        existing_critical = [col for col in critical_columns if col in df_clean.columns]
        df_clean = df_clean.dropna(subset=existing_critical)
        
        return df_clean
    
    @staticmethod
    def calculate_basic_metrics(df):
        """Calcular métricas básicas del DataFrame"""
        metrics = {}
        
        if 'monto_venta' in df.columns:
            metrics['total_sales'] = df['monto_venta'].sum()
            metrics['avg_sale'] = df['monto_venta'].mean()
            metrics['median_sale'] = df['monto_venta'].median()
            metrics['total_transactions'] = len(df)
        
        if 'cliente' in df.columns:
            metrics['unique_customers'] = df['cliente'].nunique()
        
        if 'utilidad' in df.columns:
            metrics['total_profit'] = df['utilidad'].sum()
            metrics['avg_margin'] = (df['utilidad'].sum() / df['monto_venta'].sum()) * 100
        
        return metrics
    
    @staticmethod
    def detect_anomalies(df, column='monto_venta'):
        """Detectar anomalías en los datos"""
        if column not in df.columns:
            return []
        
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        return anomalies.to_dict('records')


class ValidationHelpers:
    """Helper functions para validación"""
    
    @staticmethod
    def validate_email(email):
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """Validar que el rango de fechas sea válido"""
        if start_date >= end_date:
            return False, "La fecha de inicio debe ser anterior a la fecha fin"
        
        if (end_date - start_date).days > 3650:  # 10 años máximo
            return False, "El rango de fechas no puede exceder 10 años"
        
        return True, "Rango válido"
    
    @staticmethod
    def validate_dataframe_structure(df):
        """Validar estructura mínima del DataFrame"""
        required_columns = ['fecha', 'cliente', 'producto_servicio', 'monto_venta']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Columnas requeridas faltantes: {missing_columns}"
        
        return True, "Estructura válida"
    
    @staticmethod
    def validate_file_upload(file, max_size_mb=100):
        """Validar archivo subido"""
        if file is None:
            return False, "No se ha seleccionado archivo"
        
        # Validar tamaño
        file_size = len(file.getvalue()) / (1024 * 1024)  # MB
        if file_size > max_size_mb:
            return False, f"El archivo excede el tamaño máximo de {max_size_mb}MB"
        
        # Validar extensión
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.json']
        file_extension = f".{file.name.split('.')[-1].lower()}"
        if file_extension not in allowed_extensions:
            return False, f"Formato de archivo no soportado: {file_extension}"
        
        return True, "Archivo válido"