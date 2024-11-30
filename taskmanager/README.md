# Task Management Backend (Django REST Framework)

This is the backend for the Task Management Application, built using Django and Django REST Framework (DRF). It provides a RESTful API for managing tasks.

## Features

- API for CRUD operations on tasks (Create, Read, Update, Delete)
- Pagination support
- Sorting tasks by creation date
- Search tasks by title or description

## Prerequisites

Before you begin, ensure you have the following installed:

- Python (>=3.8)
- pip (Python Package Manager)
- PostgreSQL or SQLite (Database)

## Installation Steps

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/task-management-backend.git
cd task-management-backend


Step 2: Set Up a Virtual Environment

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate


Step 3: Install Dependencies

pip install -r requirements.txt



Step 4: Configure the Database

1.Open the settings.py file in the project_name directory.

2.Update the DATABASES setting for your database. For example, using PostgreSQL:

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "db_taskmanager"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "1234"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}



Step 5: Apply Migrations

python manage.py makemigrations
python manage.py migrate


Step 6: Create a Superuser

python manage.py createsuperuser


Step 7: Run the Development Server

python manage.py runserver

