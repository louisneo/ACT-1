from django import forms
from user_management.models import Employee, PasswordPolicy

class EmployeeForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
        label='Confirm Password'
    )
    
    class Meta:
        model = Employee
        fields = [
            'first_name', 'middle_name', 'last_name', 'suffix',
            'birthdate', 'contact_number', 'address',
            'username', 'email', 'position', 'role'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'middle_name': forms.TextInput(attrs={'placeholder': 'Middle Name (Optional)'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'suffix': forms.TextInput(attrs={'placeholder': 'Suffix (Optional, e.g., Jr, Sr, III)'}),
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Contact Number'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Address'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'position': forms.TextInput(attrs={'placeholder': 'Position (Optional)'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        
        return cleaned_data


class EmployeeEditForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current password'}),
        label='New Password'
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
        label='Confirm New Password'
    )
    
    class Meta:
        model = Employee
        fields = [
            'first_name', 'middle_name', 'last_name', 'suffix',
            'birthdate', 'contact_number', 'address',
            'email', 'position', 'role', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'middle_name': forms.TextInput(attrs={'placeholder': 'Middle Name (Optional)'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'suffix': forms.TextInput(attrs={'placeholder': 'Suffix (Optional)'}),
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Contact Number'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Address'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'position': forms.TextInput(attrs={'placeholder': 'Position (Optional)'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Passwords do not match!")
        
        return cleaned_data


class PasswordPolicyForm(forms.ModelForm):
    class Meta:
        model = PasswordPolicy
        fields = [
            'min_length',
            'require_uppercase',
            'require_lowercase',
            'require_numbers',
            'require_special_chars',
            'password_expiry_days',
            'prevent_reuse_count',
            'max_failed_attempts',
            'lockout_duration_minutes'
        ]
        widgets = {
            'min_length': forms.NumberInput(attrs={'min': 1, 'max': 128}),
            'password_expiry_days': forms.NumberInput(attrs={'min': 0, 'max': 365}),
            'prevent_reuse_count': forms.NumberInput(attrs={'min': 0, 'max': 24}),
            'max_failed_attempts': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'lockout_duration_minutes': forms.NumberInput(attrs={'min': 1, 'max': 1440}),
        }
        labels = {
            'min_length': 'Minimum Password Length',
            'require_uppercase': 'Require Uppercase Letters',
            'require_lowercase': 'Require Lowercase Letters',
            'require_numbers': 'Require Numbers',
            'require_special_chars': 'Require Special Characters',
            'password_expiry_days': 'Password Expiry (Days, 0 = Never)',
            'prevent_reuse_count': 'Prevent Password Reuse (Last N passwords)',
            'max_failed_attempts': 'Maximum Failed Login Attempts',
            'lockout_duration_minutes': 'Account Lockout Duration (Minutes)',
        }