"""
Utility functions and decorators for the CuriousBooks API
"""
from .auth import manager_required, role_required
from .tax import calculate_tax

__all__ = ['manager_required', 'role_required', 'calculate_tax']

