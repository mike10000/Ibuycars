"""
Authorization decorators for role-based access control
"""
from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user
import auth as auth_module

def manager_required(f):
    """
    Decorator to require manager role.
    Usage: @manager_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not auth_module.is_manager(current_user):
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """
    Decorator to require specific role.
    Usage: @role_required('manager')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != required_role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
