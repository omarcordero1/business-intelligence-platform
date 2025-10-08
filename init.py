# src/modules/__init__.py
from .dashboard import DashboardModule
from .sales_copilot import SalesCopilotModule
from .data_connectors import DataConnectorsModule
from .reporting import ReportingModule
from .alerts import AlertsModule

__all__ = [
    'DashboardModule',
    'SalesCopilotModule', 
    'DataConnectorsModule',
    'ReportingModule',
    'AlertsModule'
]