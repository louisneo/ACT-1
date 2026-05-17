from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def mask_email(email: str) -> str:
    if not email or '@' not in email:
        return ''
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '*'*(len(local)-1)
    else:
        masked_local = local[0] + '*'*(len(local)-2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    if not phone:
        return ''
    digits = ''.join([c for c in phone if c.isdigit()])
    if len(digits) <= 4:
        return '*' * len(digits)
    return '*'*(len(digits)-4) + digits[-4:]


def role_required(allowed_roles):
    """Decorator to require login and specific roles stored in session.

    Usage: @role_required(['admin', 'global_admin'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            emp_id = request.session.get('employee_id')
            emp_role = request.session.get('employee_role')
            if not emp_id:
                return redirect('login')
            if emp_role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('user_dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
