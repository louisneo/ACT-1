from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin pages
    path('home/', views.home, name='home'),
    path('addUser/', views.addUser, name='addUser'),
    path('editUser/<int:user_id>/', views.editUser, name='editUser'),
    path('deleteUser/<int:user_id>/', views.deleteUser, name='deleteUser'),
    path('activateUser/<int:user_id>/', views.activateUser, name='activateUser'),
    path('password-policy/', views.passwordPolicy, name='password_policy'),
    
    # User pages
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),

    # Password reset (employee-facing)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # API endpoints
    path('api/employees/', views.api_get_employees, name='api_get_employees'),
    path('api/employee/<int:user_id>/', views.api_get_employee, name='api_get_employee'),
]