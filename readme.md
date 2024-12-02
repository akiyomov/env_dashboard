# 🌍 Environmental Data Dashboard

## 🎓 University Information

**Inha University 2024 fall**  
Department: SGCS  
Major: ISE (Integrated System Engineering)  
**Course: Database Design [202402-ISE3235-001]**

## 📋 Project Information

**Project Name**: Environmental Data Dashboard  
A comprehensive system for monitoring and analyzing environmental metrics including air quality, temperature, and humidity across different locations.

### 👥 Group Members

- Kiyomov Asadbek (12225264)
-
-
-

## 🔍 Project Overview

The Environmental Data Dashboard is a database-driven web application that allows users to monitor environmental metrics across various locations. The system includes features for tracking air quality indices, setting up alerts for environmental conditions, and analyzing historical data through various types of queries.

### ⭐ Key Features

- 📊 Real-time environmental metrics monitoring
- 💨 Air Quality Index (AQI) tracking
- 🚨 Alert system for threshold violations
- 📈 Historical data analysis
- 📝 Complex SQL query demonstrations
- 📊 Interactive data visualization

## 💻 Technical Requirements

- Python 3.8+
- Django 5.0
- PostgreSQL/SQLite
- Additional Python packages as listed in requirements.txt

## 🚀 Installation and Setup

### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd env_dashboard
```

### 2️⃣ Create and Activate Virtual Environment

```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Setup

Create a .env file in the project root and add the following:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

### 5️⃣ Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

### 7️⃣ Populate Sample Data

```bash
python manage.py populate_sample_data
```

### 8️⃣ Run Development Server

```bash
python manage.py runserver
```

Access the application at: <http://localhost:8000>

## 📁 Project Structure

```
env_dashboard/
├── manage.py
├── requirements.txt
├── env_dashboard/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dashboard/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── dashboard/
└── static/
    └── dashboard/
        ├── css/
        └── js/
```

## 🗃️ Database Schema

The project implements the following database models:

- 📍 Location (city, country, coordinates)
- 📏 Metric (environmental measurements)
- 🔔 Alert (threshold notifications)
- 🌡️ AirQualityIndex (AQI measurements)

## 🛠️ Features Implementation

1. **💾 Data Management**
   - CRUD operations for all entities
   - Bulk data import/export
   - Data validation and constraints

2. **🔍 Query Functionalities**
   - Complex JOIN operations
   - Aggregate functions with GROUP BY
   - Subqueries for data analysis

3. **🎨 User Interface**
   - Responsive dashboard design
   - Interactive data visualization
   - Real-time updates

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📜 License

This project is part of the Database Design course at Inha University and is intended for educational purposes.

## 🙏 Acknowledgments

- 👨‍🏫 Course Professor
- 👨‍🏫 Teaching Assistants
- 🏫 Department of ISE, SGCS
