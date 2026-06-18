# Django Project Setup Guide

## 1. Install Python
Download and install Python from the official website:

https://www.python.org/downloads/

Verify installation:

```bash
python --version
```
or

```bash
python3 --version
```

---

## 2. Create a Virtual Environment

Navigate to the project directory:

```bash
cd project_directory
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

### Windows
```bash
venv\Scripts\activate
```

### Linux / macOS
```bash
source venv/bin/activate
```

---

## 3. Install All Requirements

Install dependencies from the requirements file:

```bash
pip install -r requirements.txt
```

Verify installed packages:

```bash
pip list
```

---

## 4. Run Database Migrations

Create migration files:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

---

## 5. Create a Superuser

Create an admin account:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:

- Username
- Email
- Password

---

## 6. Run the Django Project

Start the development server:

```bash
python manage.py runserver
```

Open your browser and visit:

```
http://127.0.0.1:8000/
```

Admin Panel:

```
http://127.0.0.1:8000/admin/
```

---

## Complete Setup Commands (Quick Start)

```bash
# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```
