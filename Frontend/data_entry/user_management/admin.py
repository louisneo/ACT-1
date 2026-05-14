from django.contrib import admin, messages
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from user_management.models import Employee, PasswordPolicy, PasswordHistory


class EmployeeAdminForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text='Leave blank to keep the current password.'
    )

    class Meta:
        model = Employee
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Do not populate the password field with the hashed value
        self.fields['password'].initial = ''

    def save(self, commit=True):
        password = self.cleaned_data.get('password')
        instance = super().save(commit=False)
        if password:
            instance.set_password(password)
        else:
            # preserve existing hashed password when no new password provided
            if self.instance and self.instance.pk:
                instance.password = self.instance.password
        if commit:
            instance.save()
        return instance

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm
    list_display = ['id', 'username', 'get_full_name', 'email', 'role', 'is_active', 'last_login', 'created_at']
    list_filter = ['role', 'is_active', 'account_locked', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    readonly_fields = ['last_login', 'last_password_update', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'suffix', 'birthdate', 'address')
        }),
        ('Contact Information', {
            'fields': ('email', 'contact_number')
        }),
        ('Account Information', {
            'fields': ('username', 'password', 'role', 'position')
        }),
        ('Security', {
            'fields': ('last_login', 'last_password_update', 'password_expiry_days', 
                      'failed_login_attempts', 'account_locked', 'locked_until')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    actions = ['send_password_reset_email']

    def send_password_reset_email(self, request, queryset):
        sent = 0
        missing = []
        for obj in queryset:
            email = getattr(obj, 'email', None)
            if not email:
                missing.append(obj.username)
                continue
            form = PasswordResetForm({'email': email})
            if form.is_valid():
                form.save(request=request, use_https=request.is_secure())
                sent += 1
        if sent:
            messages.success(request, f"Sent password reset email to {sent} user(s).")
        if missing:
            messages.warning(request, f"Selected users without email: {', '.join(missing)}")
    send_password_reset_email.short_description = 'Send password reset email to selected users'

@admin.register(PasswordPolicy)
class PasswordPolicyAdmin(admin.ModelAdmin):
    list_display = ['id', 'min_length', 'password_expiry_days', 'max_failed_attempts', 'updated_at']
    
    fieldsets = (
        ('Complexity Requirements', {
            'fields': ('min_length', 'require_uppercase', 'require_lowercase', 
                      'require_numbers', 'require_special_chars')
        }),
        ('Expiry & Lockout', {
            'fields': ('password_expiry_days', 'max_failed_attempts', 'lockout_duration_minutes')
        }),
        ('Password History', {
            'fields': ('prevent_reuse_count',)
        }),
    )

@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'created_at']
    list_filter = ['created_at']
    search_fields = ['employee__username', 'employee__first_name', 'employee__last_name']
    readonly_fields = ['employee', 'password_hash', 'created_at']