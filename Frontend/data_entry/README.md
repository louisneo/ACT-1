# Secure Employee Management System

A Django-based employee management system with role-based access control, secure password handling, and modern UI/UX design.

## 🔐 Security Features

- **Role-Based Access Control (RBAC)**: User, Admin, and Global Admin roles
- **Password Hashing**: PBKDF2-SHA256 with automatic salting
- **Password Policy Enforcement**: Minimum length, complexity requirements
- **Information Masking**: Sensitive data (email, phone) masked in UI
- **Session-Based Authentication**: Secure session management
- **CSRF Protection**: Django's built-in CSRF tokens on all forms
- **Password Reset Flow**: Self-service password reset via email
- **Account Lockout**: Automatic lockout after failed login attempts
- **Password Expiration**: Configurable password expiration policy

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd data_entry
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Important Environment Variables:**
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_BACKEND`: Email backend configuration
- `EMAIL_HOST_USER`: Email account for sending password reset emails
- `EMAIL_HOST_PASSWORD`: Email account password or app password

### 5. Create Database
```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## 📁 Project Structure

```
data_entry/
├── user_management/          # Main app
│   ├── models.py            # Employee, PasswordPolicy models
│   ├── views.py             # View logic
│   ├── forms.py             # User forms
│   ├── utils.py             # Utility functions (RBAC, masking)
│   ├── urls.py              # URL routing
│   ├── admin.py             # Django admin customization
│   ├── templates/           # HTML templates
│   │   ├── user_dashboard.html
│   │   ├── home.html
│   │   ├── login.html
│   │   └── registration/
│   └── migrations/          # Database migrations
├── data_entry/
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI application
├── manage.py                # Django management
├── db.sqlite3               # SQLite database (dev only)
├── .env                     # Environment variables (Git ignored)
├── .env.example             # Example environment file
├── .gitignore               # Git ignore rules
└── requirements.txt         # Python dependencies
```

## 👥 User Roles

### 1. **Regular User**
- View own profile and dashboard
- Change own password
- Reset password via email
- View password expiration status

### 2. **Admin**
- Manage all employees
- Add/edit/delete employees
- Configure password policy
- View password history
- Send password reset emails
- Access Django admin panel

### 3. **Global Admin**
- Full access to all admin functions
- System-wide settings management
- Employee role assignment

## 🔑 Default Credentials (Development)

After running migrations and creating a superuser, use those credentials to login.

## 🛡️ Security Best Practices

### Before Production Deployment

1. **Change SECRET_KEY**: Generate a new Django secret key
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Set DEBUG=False**: Disable debug mode
   ```
   DEBUG=False
   ```

3. **Configure ALLOWED_HOSTS**: Set your domain names
   ```
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

4. **Use PostgreSQL**: For production, switch from SQLite
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_db_name',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'your_db_host',
           'PORT': '5432',
       }
   }
   ```

5. **Configure Email**: Set up real SMTP for password reset
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

6. **Use HTTPS**: Always use HTTPS in production
   ```
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

7. **Use Environment Variables**: Never commit sensitive data
   - All secrets are in `.env` (Git ignored)
   - See `.env.example` for required variables

## 📊 Key Features

### Employee Management
- Add, edit, delete, and deactivate employees
- Search employees by name, username, email, or position
- View employee statistics (active users, admins, etc.)
- Role assignment (User, Admin, Global Admin)

### Password Management
- Secure password hashing with PBKDF2-SHA256
- Configurable password policy
- Self-service password reset
- Password expiration enforcement
- Failed login attempt tracking
- Account lockout protection

### User Interface
- Modern fullscreen dashboards with sidebar navigation
- Responsive design (mobile-friendly)
- Color-coded status badges
- Real-time search functionality
- Interactive employee table with actions

### Security & Privacy
- Information masking (email, phone number)
- Session-based authentication
- CSRF protection on all forms
- Admin action logging
- Password change history tracking

## 🧪 Testing

Run Django tests:
```bash
python manage.py test user_management
```

## 📝 Admin Panel

Access Django admin at `http://localhost:8000/admin/`:
- Manage employees
- Configure password policies
- View password history
- Send bulk password reset emails

## 🔗 Important URLs

| URL | Purpose | Access |
|-----|---------|--------|
| `/` | Login | Public |
| `/dashboard/` | User dashboard | Authenticated |
| `/home/` | Admin dashboard | Admin only |
| `/addUser/` | Add employee | Admin only |
| `/editUser/<id>/` | Edit employee | Admin only |
| `/password-policy/` | Password policy | Admin only |
| `/password-reset/` | Reset password | Public |
| `/admin/` | Django admin | Admin only |

## 🐛 Troubleshooting

### Import Error: `ModuleNotFoundError: No module named 'django'`
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

### Database Errors
- Run migrations: `python manage.py migrate`
- Reset database: `python manage.py flush` (deletes all data)

### Email Not Sending
- Check `EMAIL_BACKEND` in `.env`
- For Gmail: Use "App Passwords" instead of regular password
- Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`

### Static Files Not Loading
```bash
python manage.py collectstatic
```

## 📄 License

[Your License Here]

## 👨‍💻 Contributors

[Your Name/Team]

## 📞 Support

For issues and questions, please create an issue on GitHub.

---

**Last Updated**: May 17, 2026
