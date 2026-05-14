from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from user_management.models import Employee, PasswordPolicy, PasswordHistory
from user_management.forms import EmployeeForm, EmployeeEditForm, PasswordPolicyForm
from django.db.models import Q


# ============= AUTHENTICATION VIEWS =============

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            employee = Employee.objects.get(username=username, is_active=True)
            
            # Check if account is locked
            if employee.is_locked():
                messages.error(request, f'Account is locked. Please try again later.')
                return render(request, 'login.html')
            
            # Check password
            if employee.check_password(password):
                # Check if password expired
                if employee.is_password_expired():
                    messages.warning(request, 'Your password has expired. Please contact admin.')
                    return render(request, 'login.html')
                
                # Successful login
                employee.update_last_login()
                request.session['employee_id'] = employee.id
                request.session['employee_username'] = employee.username
                request.session['employee_role'] = employee.role
                
                messages.success(request, f'Welcome back, {employee.get_full_name()}!')
                
                # Redirect based on role
                if employee.role in ['admin', 'global_admin']:
                    return redirect('home')
                else:
                    return redirect('user_dashboard')
            else:
                # Wrong password
                employee.increment_failed_login()
                messages.error(request, 'Invalid username or password!')
                
        except Employee.DoesNotExist:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'login.html')


def logout_view(request):
    """Handle user logout"""
    request.session.flush()
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')


def user_dashboard(request):
    """Dashboard for regular users"""
    if 'employee_id' not in request.session:
        return redirect('login')
    
    employee = get_object_or_404(Employee, id=request.session['employee_id'])
    
    context = {
        'employee': employee,
    }
    return render(request, 'user_dashboard.html', context)


# ============= ADMIN VIEWS =============

def home(request):
    """Display all active and deactivated employees - Admin only"""
    if 'employee_id' not in request.session:
        return redirect('login')
    
    current_user = Employee.objects.get(id=request.session['employee_id'])
    if current_user.role not in ['admin', 'global_admin']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('user_dashboard')
    
    search_query = request.GET.get('search', '')
    
    if search_query:
        employees = Employee.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(middle_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(position__icontains=search_query)
        )
    else:
        employees = Employee.objects.all()
    
    active_employees = employees.filter(is_active=True)
    deactivated_employees = employees.filter(is_active=False)
    
    # Calculate role counts
    user_count = active_employees.filter(role='user').count()
    admin_count = active_employees.filter(role='admin').count()
    global_admin_count = active_employees.filter(role='global_admin').count()
    
    context = {
        'active_employees': active_employees,
        'deactivated_employees': deactivated_employees,
        'search_query': search_query,
        'user_count': user_count,
        'admin_count': admin_count,
        'global_admin_count': global_admin_count,
        'current_user': current_user,
    }
    return render(request, 'home.html', context)


def addUser(request):
    """Add new employee with password policy validation - Admin only"""
    if 'employee_id' not in request.session:
        return redirect('login')
    
    current_user = Employee.objects.get(id=request.session['employee_id'])
    if current_user.role not in ['admin', 'global_admin']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('user_dashboard')
    
    policy = PasswordPolicy.get_current_policy()
    
    # Get active employees and calculate counts
    active_employees = Employee.objects.filter(is_active=True)
    user_count = active_employees.filter(role='user').count()
    admin_count = active_employees.filter(role='admin').count()
    global_admin_count = active_employees.filter(role='global_admin').count()
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        
        if form.is_valid():
            # Get password before saving
            raw_password = form.cleaned_data['password']
            
            # Validate password against policy
            password_errors = policy.validate_password(raw_password)
            if password_errors:
                for error in password_errors:
                    messages.error(request, error)
                return render(request, 'addUser.html', {
                    'form': form, 
                    'policy': policy,
                    'active_employees': active_employees,
                    'user_count': user_count,
                    'admin_count': admin_count,
                    'global_admin_count': global_admin_count,
                })
            
            # Check if username or email already exists
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            
            if Employee.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
                return render(request, 'addUser.html', {
                    'form': form, 
                    'policy': policy,
                    'active_employees': active_employees,
                    'user_count': user_count,
                    'admin_count': admin_count,
                    'global_admin_count': global_admin_count,
                })
            
            if Employee.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists!')
                return render(request, 'addUser.html', {
                    'form': form, 
                    'policy': policy,
                    'active_employees': active_employees,
                    'user_count': user_count,
                    'admin_count': admin_count,
                    'global_admin_count': global_admin_count,
                })
            
            # Save employee
            employee = form.save(commit=False)
            employee.set_password(raw_password)
            employee.password_expiry_days = policy.password_expiry_days
            employee.save()
            
            # Save password to history
            PasswordHistory.objects.create(
                employee=employee,
                password_hash=employee.password
            )
            
            messages.success(request, f'User {username} created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm()
    
    return render(request, 'addUser.html', {
        'form': form, 
        'policy': policy,
        'active_employees': active_employees,
        'user_count': user_count,
        'admin_count': admin_count,
        'global_admin_count': global_admin_count,
    })


def editUser(request, user_id):
    """Edit existing employee - Admin only"""
    if 'employee_id' not in request.session:
        return redirect('login')
    
    current_user = Employee.objects.get(id=request.session['employee_id'])
    if current_user.role not in ['admin', 'global_admin']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('user_dashboard')
    
    employee = get_object_or_404(Employee, id=user_id)
    policy = PasswordPolicy.get_current_policy()
    
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=employee)
        
        if form.is_valid():
            # Check if password is being changed
            new_password = form.cleaned_data.get('new_password')
            
            if new_password:
                # Validate new password
                password_errors = policy.validate_password(new_password)
                if password_errors:
                    for error in password_errors:
                        messages.error(request, error)
                    return render(request, 'editUser.html', {
                        'form': form, 
                        'employee': employee, 
                        'policy': policy
                    })
                
                # Check password history
                if not PasswordHistory.can_use_password(employee, new_password):
                    messages.error(request, f'You cannot reuse your last {policy.prevent_reuse_count} passwords!')
                    return render(request, 'editUser.html', {
                        'form': form, 
                        'employee': employee, 
                        'policy': policy
                    })
                
                # Set new password
                employee.set_password(new_password)
                
                # Save to history
                PasswordHistory.objects.create(
                    employee=employee,
                    password_hash=employee.password
                )
            
            # Save other changes
            form.save()
            messages.success(request, f'User {employee.username} updated successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeEditForm(instance=employee)
    
    return render(request, 'editUser.html', {
        'form': form, 
        'employee': employee, 
        'policy': policy
    })


@require_http_methods(["POST"])
def deleteUser(request, user_id):
    """Soft delete (deactivate) user - Admin only"""
    if 'employee_id' not in request.session:
        return redirect('login')
    
    try:
        current_user = Employee.objects.get(id=request.session['employee_id'])
    except Employee.DoesNotExist:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('login')
    
    if current_user.role not in ['admin', 'global_admin']:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('user_dashboard')
    
    employee = get_object_or_404(Employee, id=user_id)
    
    # Prevent regular admins from deactivating other admins or global admins
    if current_user.role == 'admin' and employee.role in ['admin', 'global_admin']:
        messages.error(request, 'You cannot deactivate other administrators!')
        return redirect('home')
    
    # Prevent deactivating yourself
    if current_user.id == employee.id:
        messages.error(request, 'You cannot deactivate your own account!')
        return redirect('home')
    
    # Proceed with deactivation
    employee.is_active = False
    employee.save()
    messages.success(request, f'User {employee.username} deactivated successfully!')
    return redirect('home')


@require_http_methods(["POST"])
def activateUser(request, user_id):
    """Reactivate deactivated user - Admin only"""
    if 'employee_id' not in request.session:
        return redirect('login')
    
    try:
        current_user = Employee.objects.get(id=request.session['employee_id'])
    except Employee.DoesNotExist:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('login')
    
    if current_user.role not in ['admin', 'global_admin']:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('user_dashboard')
    
    employee = get_object_or_404(Employee, id=user_id)
    
    # Prevent regular admins from activating other admins or global admins
    if current_user.role == 'admin' and employee.role in ['admin', 'global_admin']:
        messages.error(request, 'You cannot activate other administrators!')
        return redirect('home')
    
    # Proceed with activation
    employee.is_active = True
    employee.account_locked = False
    employee.failed_login_attempts = 0
    employee.locked_until = None
    employee.save()
    messages.success(request, f'User {employee.username} activated successfully!')
    return redirect('home')


def passwordPolicy(request):
    """Manage password policy settings - Admin only"""
    if 'employee_id' not in request.session:
        return redirect('login')
    
    current_user = Employee.objects.get(id=request.session['employee_id'])
    if current_user.role not in ['admin', 'global_admin']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('user_dashboard')
    
    policy = PasswordPolicy.get_current_policy()
    
    if request.method == 'POST':
        form = PasswordPolicyForm(request.POST, instance=policy)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Password policy updated successfully!')
            return redirect('password_policy')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordPolicyForm(instance=policy)
    
    return render(request, 'password_policy.html', {'form': form, 'policy': policy})


# ============= API VIEWS =============

def api_get_employees(request):
    """API endpoint to get all employees as JSON"""
    if 'employee_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    search = request.GET.get('search', '')
    active_only = request.GET.get('active_only', 'true').lower() == 'true'
    
    employees = Employee.objects.all()
    
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) |
            Q(middle_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )
    
    if active_only:
        employees = employees.filter(is_active=True)
    
    data = []
    for emp in employees:
        data.append({
            'id': emp.id,
            'full_name': emp.get_full_name(),
            'first_name': emp.first_name,
            'middle_name': emp.middle_name or '',
            'last_name': emp.last_name,
            'suffix': emp.suffix or '',
            'username': emp.username,
            'email': emp.email,
            'contact_number': emp.contact_number or '',
            'position': emp.position or '',
            'role': emp.get_role_display(),
            'role_value': emp.role,
            'birthdate': emp.birthdate.strftime('%Y-%m-%d') if emp.birthdate else '',
            'address': emp.address or '',
            'last_login': emp.last_login.strftime('%Y-%m-%d %H:%M') if emp.last_login else 'Never',
            'last_password_update': emp.last_password_update.strftime('%Y-%m-%d') if emp.last_password_update else '',
            'password_expired': emp.is_password_expired(),
            'days_until_expiry': emp.days_until_password_expires(),
            'is_locked': emp.is_locked(),
            'is_active': emp.is_active,
            'created_at': emp.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({'employees': data})


def api_get_employee(request, user_id):
    """API endpoint to get single employee"""
    if 'employee_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    employee = get_object_or_404(Employee, id=user_id)
    
    data = {
        'id': employee.id,
        'full_name': employee.get_full_name(),
        'first_name': employee.first_name,
        'middle_name': employee.middle_name or '',
        'last_name': employee.last_name,
        'suffix': employee.suffix or '',
        'username': employee.username,
        'email': employee.email,
        'contact_number': employee.contact_number or '',
        'position': employee.position or '',
        'role': employee.role,
        'birthdate': employee.birthdate.strftime('%Y-%m-%d') if employee.birthdate else '',
        'address': employee.address or '',
        'last_login': employee.last_login.strftime('%Y-%m-%d %H:%M') if employee.last_login else 'Never',
        'is_active': employee.is_active,
    }
    
    return JsonResponse(data)