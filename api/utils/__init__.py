"""
Utility functions and decorators for the CuriousBooks API
"""
from .auth import (
    admin_required,
    manager_required,
    product_manager_required,
    role_required,
)
from .tax import calculate_tax

__all__ = [
    'admin_required',
    'manager_required',
    'product_manager_required',
    'role_required',
    'calculate_tax',
]

