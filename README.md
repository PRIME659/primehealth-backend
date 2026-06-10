# PrimeHealth API Backend

A comprehensive Django REST API for a healthcare platform supporting doctors, patients, pharmacists, and admins.

## Features

- **User Management**: Registration, authentication, profiles with role-based access
- **Doctor Management**: Doctor listings, availability, time slots, consultation booking
- **Patient Portal**: Appointment booking, rescheduling, order history
- **Pharmacy System**: Drug inventory, shopping cart, order management
- **Admin Dashboard**: Analytics, user/doctor/drug/appointment management
- **Medical Tips**: Health education content
- **Clinical Notes**: Doctor consultation notes and follow-ups
- **Security**: JWT authentication, session management, account locking on failed login

## Tech Stack

- Django 6.0
- Django REST Framework
- JWT Authentication (SimpleJWT)
- PostgreSQL/SQLite
- CORS support
- Whitenoise for static files
- Google Gemini API (Chatbot)

## Installation

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone and setup environment**
```bash
git clone <repo-url>
cd primehealth-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

Server runs on `http://localhost:8000`

## API Documentation

### Authentication Endpoints

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/logout/` - Logout and blacklist token
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get current user profile
- `PUT /api/auth/profile/update/` - Update profile
- `POST /api/auth/password/change/` - Change password

### Doctor Portal

- `GET /api/doctors/` - List all doctors
- `GET /api/doctors/<id>/` - Get doctor details
- `GET /api/doctors/specialties/` - Get all specialties
- `GET /api/doctor/dashboard/` - Doctor dashboard stats
- `GET /api/doctor/appointments/` - List doctor's appointments
- `PUT /api/doctor/appointments/<id>/update/` - Update appointment status
- `POST /api/doctor/appointments/<id>/notes/` - Add clinical note
- `GET /api/doctor/notes/` - Get clinical notes
- `PUT /api/doctor/availability/` - Update availability status
- `GET /api/doctor/time-slots/` - Get time slots
- `POST /api/doctor/time-slots/` - Create time slot
- `GET /api/doctor/profile/` - Get doctor profile
- `PUT /api/doctor/profile/` - Update doctor profile

### Pharmacist Portal

- `GET /api/pharmacist/dashboard/` - Pharmacist dashboard
- `GET /api/pharmacist/drugs/` - List all drugs
- `PUT /api/pharmacist/drugs/<id>/stock/` - Update drug stock
- `GET /api/pharmacist/orders/` - List all orders
- `PUT /api/pharmacist/orders/<id>/update/` - Update order status

### Patient Endpoints

- `GET /api/appointments/` - List user's appointments
- `POST /api/appointments/book/` - Book appointment
- `GET /api/appointments/<id>/` - Get appointment details
- `PUT /api/appointments/<id>/reschedule/` - Reschedule appointment
- `PUT /api/appointments/<id>/cancel/` - Cancel appointment
- `GET /api/pharmacy/` - List drugs
- `GET /api/pharmacy/<id>/` - Get drug details
- `GET /api/pharmacy/categories/` - Get drug categories
- `GET /api/cart/` - Get shopping cart
- `POST /api/cart/add/` - Add to cart
- `PUT /api/cart/<id>/update/` - Update cart item quantity
- `DELETE /api/cart/<id>/remove/` - Remove from cart
- `DELETE /api/cart/clear/` - Clear cart
- `POST /api/orders/place/` - Place drug order
- `GET /api/orders/history/` - Get order history

### Medical Tips

- `GET /api/tips/` - List medical tips
- `GET /api/tips/daily/` - Get daily tip (random)
- `GET /api/tips/<id>/` - Get tip details

### Admin Portal

- `GET /api/admin-portal/dashboard/` - Admin dashboard
- `GET /api/admin-portal/analytics/` - Analytics data
- `GET /api/admin-portal/users/` - List users
- `GET /api/admin-portal/users/<id>/` - Get user details
- `PUT /api/admin-portal/users/<id>/toggle/` - Toggle user active status
- `POST /api/admin-portal/doctors/create/` - Create doctor
- `PUT /api/admin-portal/doctors/<id>/update/` - Update doctor
- `DELETE /api/admin-portal/doctors/<id>/delete/` - Delete doctor
- `GET /api/admin-portal/appointments/` - List appointments
- `PUT /api/admin-portal/appointments/<id>/update/` - Update appointment
- `POST /api/admin-portal/drugs/create/` - Create drug
- `PUT /api/admin-portal/drugs/<id>/update/` - Update drug
- `DELETE /api/admin-portal/drugs/<id>/delete/` - Delete drug
- `POST /api/admin-portal/tips/create/` - Create medical tip
- `PUT /api/admin-portal/tips/<id>/update/` - Update tip
- `DELETE /api/admin-portal/tips/<id>/delete/` - Delete tip

### Chatbot

- `POST /api/chatbot/` - Send message to AI assistant

## Request Examples

### Register
```json
POST /api/auth/register/
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123",
  "role": "patient"
}
```

### Login
```json
POST /api/auth/login/
{
  "email": "john@example.com",
  "password": "securepass123"
}
```

### Book Appointment
```json
POST /api/appointments/book/
{
  "doctor_id": 1,
  "date": "2024-12-25",
  "time": "14:30",
  "description": "Check-up"
}
```

## User Roles

- **Patient**: Book appointments, order drugs, view medical tips
- **Doctor**: Manage appointments, add clinical notes, manage time slots
- **Pharmacist**: Manage drug inventory, process orders
- **Admin**: Manage all users, doctors, drugs, analytics
- **Super Admin**: Full system access

## Security Features

- JWT token-based authentication
- Session management with unique session IDs
- Account locking after 5 failed login attempts (30 min lockout)
- SSL/HTTPS enforced in production
- CORS configured for frontend
- Token blacklisting on logout
- Password validation

## Database Models

- **User**: Django's built-in user model
- **UserProfile**: Extended user information with role
- **Doctor**: Doctor information and availability
- **DoctorProfile**: Additional doctor credentials
- **DoctorTimeSlot**: Doctor availability schedule
- **Drug**: Pharmacy inventory
- **CartItem**: Shopping cart items
- **Appointment**: Doctor appointment bookings
- **ClinicalNote**: Doctor consultation notes
- **DrugOrder**: Pharmacy order history
- **MedicalTip**: Health education content

## Admin Interface

Access Django admin at `/admin/` with superuser credentials.

## Environment Variables

See `.env.example` for all required variables.

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in .env
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Setup PostgreSQL database
- [ ] Configure `GEMINI_API_KEY`
- [ ] Enable SSL/HTTPS
- [ ] Setup email backend
- [ ] Run `python manage.py collectstatic`

## Common Issues

**CORS errors**: Check `FRONTEND_URL` in .env matches frontend domain

**Database errors**: Ensure `DATABASE_URL` is valid and migrations are applied

**Authentication errors**: Check JWT token format and session validity

## Support

For issues or feature requests, please create an issue in the repository.
