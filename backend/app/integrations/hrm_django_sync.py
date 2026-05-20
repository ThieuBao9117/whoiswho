"""
Django HRM - CSB Connection Integration

This module provides utilities for HRM Django to:
1. Generate JWT tokens for CSB Connection SSO
2. Sync employee data to CSB via API
3. Handle redirect to CSB with authentication

Add this to your HRM Django project.
"""
"""
NOTE: This file is a Django integration helper intended to be deployed
to the HRM Django project — NOT part of the FastAPI app.
All Django/PyJWT imports are kept lazy (inside functions) to avoid
ImportError when this module is scanned in the FastAPI environment.
"""
import datetime
import requests


# ============================================================
# Configuration - Add these to your Django settings.py
# ============================================================

# CSB_CONNECTION_CONFIG = {
#     "BASE_URL": "http://localhost:8000",  # or production URL
#     "SHARED_SECRET_KEY": "your-shared-secret-key",  # MUST match CSB .env
#     "JWT_ALGORITHM": "HS256",
#     "JWT_EXPIRE_HOURS": 720,  # 30 days
#     "SYNC_API_KEY": "optional-api-key-for-sync",  # if you add auth to sync endpoint
# }


def generate_csb_token(user):
    """
    Generate JWT token for CSB Connection SSO.
    
    Usage in Django view:
        token = generate_csb_token(request.user)
        return redirect(f"{CSB_BASE_URL}/?token={token}")
    
    Args:
        user: Django User instance (auth_user)
    
    Returns:
        str: JWT token
    """
    import jwt  # PyJWT — available in HRM Django env
    from django.conf import settings

    csb_config = getattr(settings, 'CSB_CONNECTION_CONFIG', {})
    secret_key = csb_config.get('SHARED_SECRET_KEY', settings.SECRET_KEY)
    algorithm = csb_config.get('JWT_ALGORITHM', 'HS256')
    expire_hours = csb_config.get('JWT_EXPIRE_HOURS', 720)

    payload = {
        "sub": user.username,
        "user_id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expire_hours),
        "iat": datetime.datetime.utcnow(),
        "source": "hrm"
    }

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def sync_employee_to_csb(employee):
    """
    Sync a single employee from HRM → CSB Connection.
    
    Call this when:
    - Employee is created
    - Employee info changes (dept, role, status)
    - Employee is deactivated
    
    Usage in Django signal or save method:
        sync_employee_to_csb(employee)
    
    Args:
        employee: HRM Employee model instance
    
    Returns:
        dict: Sync response from CSB API
    """
    from django.conf import settings
    
    csb_config = getattr(settings, 'CSB_CONNECTION_CONFIG', {})
    csb_base_url = csb_config.get('BASE_URL', 'http://localhost:8000')
    
    # Get related user if exists
    user = getattr(employee, 'user', None)
    
    payload = {
        "hrm_employee_id": employee.id,
        "hrm_user_id": user.id if user else None,
        "emp_code": employee.emp_code,
        "username": user.username if user else f"emp_{employee.emp_code}",
        "full_name": employee.full_name,
        "email": user.email if user else None,
        "department": getattr(employee, 'department', None),
        "part": getattr(employee, 'part', None),
        "role": getattr(employee, 'role', None),
        "status": getattr(employee, 'status', 'Active'),
        "join_date": getattr(employee, 'join_date', None).isoformat() if getattr(employee, 'join_date', None) else None,
        "photo": getattr(employee, 'photo', None),
    }
    
    try:
        response = requests.post(
            f"{csb_base_url}/api/sync/employees",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Log error but don't block HRM operations
        print(f"Failed to sync employee {employee.id} to CSB: {e}")
        return {"success": False, "error": str(e)}


def batch_sync_employees_to_csb(employees_queryset=None):
    """
    Batch sync all employees from HRM → CSB.
    
    Use for:
    - Initial setup
    - Manual re-sync
    - Scheduled sync job (cron)
    
    Usage:
        # Sync all active employees
        batch_sync_employees_to_csb(Employee.objects.filter(status='Active'))
        
        # Sync specific employees
        batch_sync_employees_to_csb(Employee.objects.filter(department='IT'))
    
    Args:
        employees_queryset: Django QuerySet of Employee instances
    
    Returns:
        dict: Batch sync response from CSB API
    """
    from django.conf import settings
    
    csb_config = getattr(settings, 'CSB_CONNECTION_CONFIG', {})
    csb_base_url = csb_config.get('BASE_URL', 'http://localhost:8000')
    
    if employees_queryset is None:
        from your_hrm_app.models import Employee  # Update with your actual app name
        employees_queryset = Employee.objects.all()
    
    payloads = []
    for employee in employees_queryset:
        user = getattr(employee, 'user', None)
        
        payloads.append({
            "hrm_employee_id": employee.id,
            "hrm_user_id": user.id if user else None,
            "emp_code": employee.emp_code,
            "username": user.username if user else f"emp_{employee.emp_code}",
            "full_name": employee.full_name,
            "email": user.email if user else None,
            "department": getattr(employee, 'department', None),
            "part": getattr(employee, 'part', None),
            "role": getattr(employee, 'role', None),
            "status": getattr(employee, 'status', 'Active'),
            "join_date": getattr(employee, 'join_date', None).isoformat() if getattr(employee, 'join_date', None) else None,
            "photo": getattr(employee, 'photo', None),
        })
    
    try:
        response = requests.post(
            f"{csb_base_url}/api/sync/employees/batch",
            json=payloads,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to batch sync employees to CSB: {e}")
        return {"success": False, "error": str(e)}


# ============================================================
# Django Views - Add these to your HRM urls.py
# ============================================================

def csb_sso_redirect(request):
    """
    Django view for SSO redirect to CSB Connection.
    
    Add to urls.py:
        path('csb/login/', csb_sso_redirect, name='csb_sso_redirect'),
    
    Usage:
        <a href="{% url 'csb_sso_redirect' %}">Go to CSB Connection</a>
    """
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login')
    
    from django.conf import settings as django_settings

    token = generate_csb_token(request.user)

    csb_config = getattr(django_settings, 'CSB_CONNECTION_CONFIG', {})
    csb_base_url = csb_config.get('BASE_URL', 'http://localhost:8000')
    
    # Redirect to CSB with token
    from django.shortcuts import redirect
    return redirect(f"{csb_base_url}/api/auth/sso-login?token={token}")


def csb_sync_selected_employees(request):
    """
    Django admin view to manually sync selected employees.
    
    Add to urls.py:
        path('admin/csb/sync/', csb_sync_selected_employees, name='csb_sync'),
    """
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        import json
        employee_ids = json.loads(request.body).get('employee_ids', [])
        
        from your_hrm_app.models import Employee  # Update with your actual app name
        employees = Employee.objects.filter(id__in=employee_ids)
        
        result = batch_sync_employees_to_csb(employees)
        return JsonResponse(result)
    
    return JsonResponse({"error": "POST required"}, status=400)
