# Patient-management-system
# Patient Management System

A secure and scalable web-based Patient Management System built with Django. This application streamlines healthcare operations by providing features for managing doctor-patient interactions, appointments, and dashboards for both administrators and medical staff.

## 🚀 Features

- User authentication with role-based access (Admin, Doctor, Patient)
- Dashboard views for patients and doctors
- Appointment scheduling and management
- Patient records management
- Secure login with input validation and CSRF protection
- Responsive front-end templates integrated with Django

## 🛠️ Tech Stack

- Python
- Django Web Framework
- SQLite (default, easily replaceable with PostgreSQL)
- Bootstrap (for front-end responsiveness)

## 🧰 Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/nsoyuka-judex/Patient-management-system.git
   cd Patient-management-system
python -m venv vrenv
source vrenv/bin/activate  # On Windows: vrenv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

