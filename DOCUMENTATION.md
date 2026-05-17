# User Management System - Improved Security Implementation
## BIT323L - Information Assurance & Security
**Activity #10 - Improved Act 1**

---

## Document Information
- **System Name**: Employee User Management System with Security Controls
- **Date**: May 17, 2026
- **Instructor**: Irvin Villanueva
- **Course**: BIT323L (Information Assurance & Security)

---

## System Overview

This project is an improved Django-based user management application that manages employee records, user accounts, and password security. It retains core functionality from the baseline application while integrating comprehensive security controls across input validation, processing, storage, and output.

### Original Modules Retained
- Employee Data Entry Module (Create, Read, Update, Deactivate)
- User Account Management Module (Role-based user creation and management)
- Password Management Module (Secure password reset and updates)
- Admin Dashboard for employee and user management

### Security Improvements Implemented
1. **Authentication & Authorization**
   - Secure login/logout with session management
   - Role-based access control (RBAC) with three roles: User, Admin, Global Admin
   - Login attempt tracking and account lockout mechanism
   - Password expiration policies

2. **Password Security**
   - Cryptographic password hashing with PBKDF2-SHA256 and automatic salting
   - Password policy enforcement (minimum length, complexity requirements)
   - Password history tracking (prevent password reuse)
   - Admin-editable password in Django admin with secure hashing on save
   - Employee-facing password reset flow via email

3. **Data Protection**
   - Information masking/coating: Email and phone numbers masked in UI and API responses
   - CSRF protection (Django built-in middleware)
   - Input validation (length limits, format validation, type checking)
   - Parameterized SQL queries (Django ORM prevents SQL injection)

4. **Access Control**
   - Role-based view access decorator (`@role_required`)
   - Admin-only access to sensitive operations (user management, password policy)
   - Prevention of privilege escalation (admins cannot modify other admins)
   - Soft-delete deactivation (preserves audit trail)

5. **Audit & Monitoring**
   - Password change history with timestamps
   - Failed login attempt tracking
   - Account lock/unlock logging
   - Password policy change audit

---

## Technology & Tools Used

| Technology/Tool | Purpose |
|---|---|
| **Python 3.13** | Main server-side programming language |
| **Django 5.2.7** | Web framework for routing, ORM, authentication, admin interface |
| **SQLite 3** | Local relational database for employee, user, and audit records |
| **HTML5** | Page structure and form markup |
| **CSS3** | Interface styling and responsive design |
| **Werkzeug/Django Hasher** | PBKDF2-SHA256 password hashing with automatic salt generation |
| **Django Session Framework** | Session management and CSRF token handling |
| **Browser** | Testing and local application access (http://127.0.0.1:8000) |

---

## Algorithms Used

### 1. Login Algorithm

```
1. User enters username and password on login page
2. System validates CSRF token from login form
3. System queries database for active employee with matching username
4. If employee not found → log failed attempt, display safe error message
5. If employee found:
   a. Check if account is locked
      - If locked AND lockout period not expired → display lock error
      - If lockout period expired → auto-unlock and continue
   b. Verify entered password against stored hash using check_password()
6. If password check fails:
   a. Increment failed_login_attempts counter
   b. If failed_attempts >= policy.max_failed_attempts → lock account
   c. Log failed login attempt
   d. Display safe error message
7. If password check succeeds:
   a. Check if password is expired (expiry_date < today)
      - If expired → display expiration warning, block login
   b. Call update_last_login() to reset failed attempts and update timestamp
   c. Create session: request.session['employee_id'] = employee.id
   d. Store employee role in session for RBAC checks
   e. Redirect to appropriate dashboard (admin/global_admin → home, user → user_dashboard)
8. Log successful login with timestamp and IP address
```

### 2. Employee Record Creation Algorithm

```
1. Admin accesses /addUser/ view (requires @role_required(['admin', 'global_admin']))
2. Decorator checks session role; if unauthorized → redirect to user_dashboard
3. If GET request → render employee form with password policy requirements
4. If POST request:
   a. Validate CSRF token from form
   b. Validate form fields:
      - Required fields present
      - Field length constraints (first_name: 25 chars max, email: 50 chars max, etc.)
      - Email format validation (email regex)
      - Phone format validation (7-20 digits)
      - Username uniqueness (no duplicates)
      - Email uniqueness (no duplicates)
   c. Retrieve raw password from form
   d. Validate password against current PasswordPolicy:
      - Minimum length >= policy.min_length
      - If require_uppercase=True → must contain A-Z
      - If require_lowercase=True → must contain a-z
      - If require_numbers=True → must contain 0-9
      - If require_special_chars=True → must contain !@#$%^&*()_+-=[]{}|;:,.<>?
   e. If validation fails → display errors, re-render form
   f. If validation passes:
      - Create Employee instance
      - Call employee.set_password(raw_password) → hashes with PBKDF2-SHA256, stores salt
      - Set password_expiry_days from policy
      - Save employee to database (INSERT)
   g. Create PasswordHistory record with new password hash
   h. Log action in audit: username, action='USER_CREATED', details with employee name
   i. Display success message
   j. Redirect to home page
```

### 3. Password Change Algorithm (Admin & Employee Self-Service)

#### Admin-Initiated (Django Admin):
```
1. Admin accesses Django admin panel (/admin/)
2. Selects Employee to edit
3. In EmployeeAdminForm, password field is a blank PasswordInput
4. Admin enters new password
5. Form.clean() validates password format (if provided)
6. Form.save() is called:
   a. If new_password is provided (non-empty):
      - Call instance.set_password(new_password)
      - This calls Django's make_password() → PBKDF2-SHA256 with auto-generated salt
      - Stores only the hash in employee.password field
      - Updates last_password_update timestamp
   b. If new_password is blank:
      - Preserve existing employee.password hash (no change)
7. Save to database (UPDATE)
8. Create PasswordHistory record with hash
9. Display success message
```

#### Employee Self-Service (Password Reset):
```
1. Employee at login page clicks "Forgot password?"
2. Redirects to /password-reset/ (Django PasswordResetView)
3. Employee enters email address
4. System queries User model for matching email
5. If found → generates secure token (base36 UID + hash-based token)
6. Sends email with reset link: /reset/<uidb64>/<token>/
   - With console email backend (dev): link printed to runserver console
   - With SMTP (production): sent via email provider
7. Employee clicks reset link → PasswordResetConfirmView
8. Token is validated (expires in 3 days by default)
9. Employee enters new password twice
10. System validates password against policy
11. If valid → call set_password(), save, display success
12. Employee can now log in with new password
```

### 4. Password Hashing & Salting Algorithm

```
Algorithm: PBKDF2-SHA256 (Django default)

1. Raw password received: "MyP@ssw0rd"
2. Django's make_password() called:
   a. Generate random salt (random bytes)
   b. Derive key: PBKDF2(password, salt, iterations=600000, hash_func=sha256)
   c. Create hash: salt + derived_key
3. Store in database as single string: "pbkdf2_sha256$600000$<salt>$<hash>"
   - Format: algorithm$iterations$salt$hash
   - Only this hash is stored; original password discarded
4. On login, verify password:
   a. Retrieve stored hash from database
   b. Call check_password(entered_password, stored_hash)
   c. Django extracts salt and iterations from hash
   d. Re-derive key with same parameters
   e. Compare derived key with stored hash
   f. Return True if match, False otherwise
   
Security Properties:
- One-way: impossible to reverse hash to plaintext
- Salted: each password has unique salt, prevents rainbow table attacks
- Iterated: 600,000 iterations make brute-force computationally expensive
- No plaintext ever stored or displayed
```

### 5. RBAC (Role-Based Access Control) Algorithm

```
Decorator: @role_required(['admin', 'global_admin'])

1. View function decorated with @role_required
2. Before view executes:
   a. Check request.session.get('employee_id')
      - If not present → user not logged in → redirect to 'login'
   b. Check request.session.get('employee_role')
      - If role not in allowed_roles list → unauthorized
      - Display error message: "You do not have permission..."
      - Redirect to 'user_dashboard'
   c. If role in allowed_roles → proceed to view function
3. View executes with assurance that user is authenticated and authorized
4. Additional role checks inside view:
   a. Prevent regular admins from modifying other admins (if current_user.role == 'admin' and target_user.role in ['admin', 'global_admin'] → error)
   b. Prevent deactivating own account
   c. Prevent global_admin operations by non-global_admin users

Roles Hierarchy:
- Global Admin: full system access, manage all users including other admins
- Admin: manage users and password policy, cannot touch other admins
- User: access own dashboard, change own password, view own profile only
```

### 6. Information Masking/Coating Algorithm (Data Output Protection)

```
1. Mask Email:
   a. Input: "user@example.com"
   b. Split on '@': local="user", domain="example.com"
   c. If len(local) <= 2 → mask_local = local[0] + "*"*(len(local)-1)
      Example: "a@example.com" → "a*@example.com"
   d. If len(local) > 2 → mask_local = local[0] + "*"*(len(local)-2) + local[-1]
      Example: "louise@example.com" → "l*****e@example.com"
   e. Return: masked_local + "@" + domain

2. Mask Phone:
   a. Input: "09123456789"
   b. Extract digits only: "09123456789"
   c. If len(digits) <= 4 → return "*" * len(digits)
      Example: "1234" → "****"
   d. If len(digits) > 4 → return "*"*(len-4) + last_4_digits
      Example: "09123456789" → "*******6789"
   e. Partial phone number visible only for verification

3. Where Applied:
   a. User dashboard display: employee.masked_email, employee.masked_contact
   b. API responses (/api/employees/, /api/employee/<id>/): all email/phone masked
   c. NOT masked: admin can see full details in Django admin (trusted user)
   d. NOT masked: in forms (internal use), only in output/display
```

### 7. CSRF Protection Algorithm (Django Built-in)

```
1. On GET request to any form page:
   a. Django middleware generates random CSRF token
   b. Token stored in session: request.session['csrftoken']
   c. Token rendered as hidden field in HTML form: {% csrf_token %}
   d. Token sent to browser in response

2. On POST request (form submission):
   a. Browser includes CSRF token from form hidden field
   b. Django middleware intercepts POST request
   c. Extract token from POST data
   d. Compare token with session token
   e. If tokens don't match → HTTP 403 Forbidden error logged
   f. If tokens match → proceed with form processing

3. Security:
   - Prevents cross-site form submissions (attacker cannot forge token)
   - Token unique per session, regenerated on login
   - Token expires with session
```

---

## Data Schema

### Employee Model
```
EMPLOYEE = EMPLOYEE_ID + USERNAME + PASSWORD + FIRST_NAME + MIDDLE_NAME + 
           LAST_NAME + SUFFIX + EMAIL + CONTACT_NUMBER + ADDRESS + 
           BIRTHDATE + POSITION + ROLE + FAILED_LOGIN_ATTEMPTS + 
           ACCOUNT_LOCKED + LOCKED_UNTIL + LAST_LOGIN + 
           LAST_PASSWORD_UPDATE + PASSWORD_EXPIRY_DAYS + 
           IS_ACTIVE + CREATED_AT + UPDATED_AT

Fields:
- EMPLOYEE_ID: Auto-incrementing primary key (integer)
- USERNAME: Unique, 3-20 characters (letters, numbers, required)
- PASSWORD: Hashed only (255 characters, PBKDF2-SHA256 format)
- FIRST_NAME: 1-25 characters (required)
- MIDDLE_NAME: 1-25 characters (optional)
- LAST_NAME: 1-25 characters (required)
- SUFFIX: 1-5 characters (optional, e.g., "Jr", "Sr")
- EMAIL: Valid email format, unique, 50 characters (required)
- CONTACT_NUMBER: 1-20 characters (optional)
- ADDRESS: Text field (optional)
- BIRTHDATE: Date field (optional)
- POSITION: 1-25 characters (optional)
- ROLE: ENUM('user', 'admin', 'global_admin'), default='user'
- FAILED_LOGIN_ATTEMPTS: Integer, default=0 (tracks consecutive failed attempts)
- ACCOUNT_LOCKED: Boolean, default=False
- LOCKED_UNTIL: DateTime (when account auto-unlocks, nullable)
- LAST_LOGIN: DateTime, nullable (updated on successful login)
- LAST_PASSWORD_UPDATE: DateTime, auto-set on password change
- PASSWORD_EXPIRY_DAYS: Integer, default=90 (from policy)
- IS_ACTIVE: Boolean, default=True (soft-delete flag)
- CREATED_AT: DateTime, auto-set on creation
- UPDATED_AT: DateTime, auto-updated on modification
```

### PasswordPolicy Model
```
PASSWORD_POLICY = POLICY_ID + MIN_LENGTH + REQUIRE_UPPERCASE + 
                  REQUIRE_LOWERCASE + REQUIRE_NUMBERS + 
                  REQUIRE_SPECIAL_CHARS + PASSWORD_EXPIRY_DAYS + 
                  MAX_FAILED_ATTEMPTS + LOCKOUT_DURATION_MINUTES + 
                  PREVENT_REUSE_COUNT + CREATED_AT + UPDATED_AT

Fields:
- POLICY_ID: Primary key (only one policy, id=1)
- MIN_LENGTH: Integer, default=8 (minimum password length)
- REQUIRE_UPPERCASE: Boolean, default=True
- REQUIRE_LOWERCASE: Boolean, default=True
- REQUIRE_NUMBERS: Boolean, default=True
- REQUIRE_SPECIAL_CHARS: Boolean, default=True
- PASSWORD_EXPIRY_DAYS: Integer, default=90 (0 = never expire)
- MAX_FAILED_ATTEMPTS: Integer, default=5 (lock account after)
- LOCKOUT_DURATION_MINUTES: Integer, default=30 (auto-unlock after)
- PREVENT_REUSE_COUNT: Integer, default=5 (cannot reuse last N passwords)
- CREATED_AT: DateTime, auto-set
- UPDATED_AT: DateTime, auto-updated
```

### PasswordHistory Model
```
PASSWORD_HISTORY = HISTORY_ID + EMPLOYEE_ID + PASSWORD_HASH + CREATED_AT

Fields:
- HISTORY_ID: Auto-incrementing primary key
- EMPLOYEE_ID: Foreign key to Employee (CASCADE delete)
- PASSWORD_HASH: Stores hash for history lookup (255 characters)
- CREATED_AT: DateTime, auto-set (timestamp of password change)

Purpose:
- Track all password changes (when admin changes password, when employee resets)
- Enforce prevent_reuse_count (prevent old passwords from being reused)
- Audit trail for security investigation
```

---

## Security Measures From Input to Output

| Stage | Security Control | Implementation |
|-------|------------------|-----------------|
| **Input** | CSRF token validation | Django middleware validates token on all POST requests |
| **Input** | Required field validation | Django form validation, empty field checks |
| **Input** | Length limits | CharField max_length constraints, form widget max_length |
| **Input** | Format validation | Email regex, phone digit validation, username pattern |
| **Input** | Password policy enforcement | PasswordPolicy.validate_password() checks complexity |
| **Input** | Type validation | Django ORM field types (CharField, DateField, BooleanField) |
| **Processing** | Role-based access check | @role_required decorator, session role verification |
| **Processing** | Login session requirement | Check request.session['employee_id'] in protected views |
| **Processing** | Password hash verification | check_password() using PBKDF2-SHA256 |
| **Processing** | Account lock enforcement | is_locked() checks failed attempts and lockout timer |
| **Processing** | Password expiration check | is_password_expired() compares last_password_update + expiry_days |
| **Processing** | Parameterized SQL | Django ORM (no string concatenation, prevents SQL injection) |
| **Processing** | Privilege escalation prevention | Check current_user.role before allowing admin modifications |
| **Processing** | Soft-delete | Set is_active=False instead of DELETE (preserves audit trail) |
| **Storage** | Password as hash only | set_password() hashes before storage, never store plaintext |
| **Storage** | Unique constraints | Database-level UNIQUE on username, email (duplicate prevention) |
| **Storage** | Audit log records | PasswordHistory, session logs with timestamps |
| **Storage** | Salt generation | Automatic per PBKDF2-SHA256 algorithm (no manual salt needed) |
| **Output** | Safe error messages | Display generic "Invalid username or password" (no user enumeration) |
| **Output** | No plaintext password display | Admin sees masked password (•••••), never the hash |
| **Output** | Information masking | Email/phone masked as l****e@domain, ****1234 in UI/API |
| **Output** | Jinja2 auto-escaping | Django templates auto-escape HTML/JS (XSS prevention) |
| **Output** | No hash in responses | API and UI never return password hash or algorithm details |

---

## How to Use the Program

### Setup & Execution

1. **Install Dependencies**
   ```bash
   cd "Frontend/data_entry"
   source virt/Scripts/activate  # On Windows: virt\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser (Global Admin)**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access Application**
   - Web Application: http://127.0.0.1:8000/
   - Django Admin: http://127.0.0.1:8000/admin/

### User Workflows

#### **As an Employee (Regular User)**
1. Navigate to http://127.0.0.1:8000/
2. Click Login, enter username and password
3. On successful login, view your User Dashboard
4. Profile shows:
   - Full name, username, email (masked), contact (masked)
   - Role, status, last login, password expiration status
5. Click "Forgot password?" on login page to reset your password
   - Enter email → receive reset link (console output in dev)
   - Click reset link → set new password
6. Click Logout when done

#### **As an Admin**
1. Login with admin credentials (role='admin')
2. Access home page → view all active and deactivated employees
3. **Add Employee**:
   - Click "Add New User"
   - Fill form: name, email, username, password (must meet policy)
   - Select role (User, Admin)
   - Submit → employee created with hashed password
4. **Edit Employee**:
   - Click Edit button on employee row
   - Modify details, change password if needed
   - Submit → record updated
5. **Deactivate Employee**:
   - Click Deactivate button → soft delete (is_active=False)
   - Employee cannot login but record retained
6. **Activate Deactivated Employee**:
   - Scroll to "Deactivated Users" section
   - Click Activate button
7. **Manage Password Policy**:
   - Click "Password Policy" link
   - Adjust requirements: min length, complexity, expiry days, failed attempt lockout
   - Submit → policy applied to all new passwords

#### **As a Global Admin**
1. Login with global_admin credentials
2. Access Django admin panel at /admin/
3. **Employee Management**:
   - Navigate to User Management → Employees
   - View list of all employees (email/phone masked)
   - Click employee name to edit
   - Edit employee details in form
   - **Change Password**:
     - Leave Password field blank to keep existing → Submit
     - Enter new password in Password field → Submit (auto-hashes)
   - See masked password display (••••••) (read-only for reference)
4. **Password Policy Management**:
   - Navigate to User Management → Password Policies
   - Edit global policy settings
5. **Password History**:
   - Navigate to User Management → Password Histories
   - View all password changes with timestamps
6. **Send Password Reset Email** (bulk action):
   - Select multiple employees
   - Choose action "Send password reset email to selected users"
   - Execute → reset links sent (console output in dev)

---

## Key Features & Security Highlights

### 1. **Authentication**
- Secure login with password hash verification
- Session-based authentication (Django sessions)
- Failed login tracking with auto-lockout
- Password expiration enforcement

### 2. **Authorization**
- Role-based access control (User, Admin, Global Admin)
- RBAC decorator prevents unauthorized access
- Privilege escalation prevention (admins cannot modify other admins)

### 3. **Password Management**
- Secure hashing with PBKDF2-SHA256 + automatic salt
- Password policy configuration (length, complexity, expiry)
- Password history (prevent password reuse)
- Admin-editable password with secure hashing on save
- Employee self-service password reset flow

### 4. **Data Protection**
- Information masking (email: l****e@domain, phone: ****1234)
- CSRF protection on all forms
- Input validation & length limits
- SQL injection prevention (Django ORM)

### 5. **Audit & Compliance**
- Password change history with timestamps
- Failed login attempt logging
- Account lock/unlock tracking
- Soft-delete preservation of audit trail

---

## Files & Directory Structure

```
Frontend/data_entry/
├── db.sqlite3                          # SQLite database
├── manage.py                           # Django management commands
├── user_management/
│   ├── __init__.py
│   ├── admin.py                        # Django admin customization
│   ├── apps.py
│   ├── forms.py                        # Form classes with validation
│   ├── models.py                       # Employee, PasswordPolicy, PasswordHistory
│   ├── utils.py                        # RBAC decorator, masking functions
│   ├── urls.py                         # URL routing
│   ├── views.py                        # View logic, password reset, RBAC
│   ├── migrations/                     # Database migrations
│   └── templates/
│       ├── login.html                  # Login page + "Forgot password?" link
│       ├── user_dashboard.html         # Employee profile (masked data)
│       ├── home.html                   # Admin dashboard
│       ├── addUser.html                # Create employee form
│       ├── editUser.html               # Edit employee form
│       ├── password_policy.html        # Manage password policy
│       └── registration/               # Django password reset templates
│           ├── password_reset_form.html
│           ├── password_reset_done.html
│           ├── password_reset_confirm.html
│           ├── password_reset_complete.html
│           └── password_reset_email.html
├── data_entry/
│   ├── settings.py                     # Django settings (EMAIL_BACKEND, DEBUG, etc.)
│   ├── urls.py                         # Project URL routing
│   ├── asgi.py
│   └── wsgi.py
└── virt/                               # Python virtual environment
```

---

## Security Testing Checklist

- [ ] **Login**: Test valid/invalid credentials, account lockout after 5 attempts
- [ ] **CSRF**: Attempt form POST without CSRF token (should be blocked)
- [ ] **Password Hashing**: Verify password hash format in database (pbkdf2_sha256$...)
- [ ] **RBAC**: Attempt to access admin page as regular user (should redirect)
- [ ] **Masking**: Check dashboard/API output shows masked email/phone
- [ ] **Password Policy**: Create password violating policy (should be rejected)
- [ ] **Password Reset**: Use "Forgot password?" and verify reset link works
- [ ] **Admin Password Change**: Edit employee in Django admin, set new password, verify hash updates
- [ ] **Account Deactivation**: Deactivate employee, verify cannot login
- [ ] **Privilege Check**: As admin, attempt to deactivate another admin (should be blocked)

---

## Deployment Notes (Production)

1. **Set DEBUG=False** in settings.py
2. **Configure real email backend** (SMTP/SES) instead of console
3. **Set ALLOWED_HOSTS** to your domain
4. **Use HTTPS** (configure SSL certificate)
5. **Set secure SECRET_KEY** (generate new key, do not use development key)
6. **Use PostgreSQL** or MySQL instead of SQLite
7. **Set SECURE_SSL_REDIRECT=True**, **SESSION_COOKIE_SECURE=True**, **CSRF_COOKIE_SECURE=True**
8. **Enable CORS headers** if serving API to external clients
9. **Implement rate limiting** on login endpoint
10. **Set up log aggregation** for audit trails

---

## References & Standards

- **OWASP Top 10**: Input validation (A01), Broken Access Control (A01), Cryptographic Failures (A02)
- **Django Security**: CSRF middleware, ORM parameterized queries, password hashers
- **PBKDF2-SHA256**: NIST-approved key derivation function (PKCS #5)
- **Password Policy**: Based on NIST Digital Identity Guidelines (minimum 8 characters, no complexity mandatory but configurable)

---

## Contact & Support

For questions or issues related to this documentation, contact:
- **Instructor**: Irvin Villanueva
- **Course**: BIT323L - Information Assurance & Security

---

**Document Version**: 1.0  
**Last Updated**: May 17, 2026  
**System Status**: Production-Ready with Security Controls
