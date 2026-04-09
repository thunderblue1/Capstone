"""
Role constants for RBAC. Do not trust role from client input; always load from DB.
"""
CUSTOMER = 'customer'
MANAGER = 'manager'   # Can add/edit/delete products
ADMIN = 'admin'

ALL_ROLES = (CUSTOMER, MANAGER, ADMIN)

# Roles that can perform product CRUD (no vertical escalation: only these roles from DB)
PRODUCT_MANAGER_ROLES = (MANAGER, ADMIN)
