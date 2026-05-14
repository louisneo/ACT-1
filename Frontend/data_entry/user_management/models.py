from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta

class PasswordPolicy(models.Model):
    """Global password policy settings"""
    # Complexity requirements
    min_length = models.IntegerField(default=8)
    require_uppercase = models.BooleanField(default=True)
    require_lowercase = models.BooleanField(default=True)
    require_numbers = models.BooleanField(default=True)
    require_special_chars = models.BooleanField(default=True)
    
    # Expiry and lockout
    password_expiry_days = models.IntegerField(default=90)
    max_failed_attempts = models.IntegerField(default=5)
    lockout_duration_minutes = models.IntegerField(default=30)
    
    # Password history
    prevent_reuse_count = models.IntegerField(default=5)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Password Policy"
        verbose_name_plural = "Password Policies"
    
    def __str__(self):
        return f"Password Policy (Updated: {self.updated_at.strftime('%Y-%m-%d')})"
    
    @classmethod
    def get_current_policy(cls):
        """Get or create the current password policy"""
        policy, created = cls.objects.get_or_create(id=1)
        return policy
    
    def validate_password(self, password):
        """Validate password against policy requirements"""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f'Password must be at least {self.min_length} characters long')
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append('Password must contain at least one uppercase letter')
        
        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append('Password must contain at least one lowercase letter')
        
        if self.require_numbers and not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one number')
        
        if self.require_special_chars and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            errors.append('Password must contain at least one special character')
        
        return errors


class Employee(models.Model):
    """Enhanced Employee model with security features"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('global_admin', 'Global Admin'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=25)
    middle_name = models.CharField(max_length=25, blank=True, null=True)
    last_name = models.CharField(max_length=25)
    suffix = models.CharField(max_length=5, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    
    # Contact Information
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True)
    
    # Account Information
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)  # Increased for hashed passwords
    position = models.CharField(max_length=25, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # Security Tracking
    last_login = models.DateTimeField(null=True, blank=True)
    last_password_update = models.DateTimeField(default=timezone.now)
    password_expiry_days = models.IntegerField(default=90)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_full_name(self):
        """Return full name with middle name and suffix"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return ' '.join(parts)
    
    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
        self.last_password_update = timezone.now()
    
    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)
    
    def update_last_login(self):
        """Update last login timestamp and reset failed attempts"""
        self.last_login = timezone.now()
        self.failed_login_attempts = 0
        self.account_locked = False
        self.locked_until = None
        self.save()
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if needed"""
        self.failed_login_attempts += 1
        policy = PasswordPolicy.get_current_policy()
        
        if self.failed_login_attempts >= policy.max_failed_attempts:
            self.account_locked = True
            self.locked_until = timezone.now() + timedelta(minutes=policy.lockout_duration_minutes)
        
        self.save()
    
    def is_password_expired(self):
        """Check if password has expired"""
        if self.last_password_update and self.password_expiry_days > 0:
            expiry_date = self.last_password_update + timedelta(days=self.password_expiry_days)
            return timezone.now() > expiry_date
        return False
    
    def is_locked(self):
        """Check if account is currently locked"""
        if self.account_locked and self.locked_until:
            if timezone.now() > self.locked_until:
                # Auto-unlock if lockout period has passed
                self.account_locked = False
                self.locked_until = None
                self.failed_login_attempts = 0
                self.save()
                return False
            return True
        return self.account_locked
    
    def days_until_password_expires(self):
        """Calculate days until password expires"""
        if self.last_password_update and self.password_expiry_days > 0:
            expiry_date = self.last_password_update + timedelta(days=self.password_expiry_days)
            days_left = (expiry_date - timezone.now()).days
            return max(0, days_left)
        return None


class PasswordHistory(models.Model):
    """Track password history to prevent reuse"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Password History"
        verbose_name_plural = "Password Histories"
    
    def __str__(self):
        return f"{self.employee.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def can_use_password(cls, employee, new_password):
        """Check if password has been used recently"""
        policy = PasswordPolicy.get_current_policy()
        recent_passwords = cls.objects.filter(
            employee=employee
        ).order_by('-created_at')[:policy.prevent_reuse_count]
        
        for history in recent_passwords:
            if check_password(new_password, history.password_hash):
                return False
        return True