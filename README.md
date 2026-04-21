# Deen & Discipline OS

A personal Islamic productivity and discipline system built with Django.
Track your prayers, manage tasks, write daily reflections, and monitor your discipline score — all in one place.

---

## Features

- **User Authentication** — Register, login, and logout securely
- **Task Management** — Create tasks, mark them complete, track daily progress
- **Prayer Tracking** — Log all 5 daily prayers with completed and on-time status
- **Daily Journal** — Write a daily reflection and rate your day (1–10)
- **Discipline Score** — Auto-computed daily score out of 100 based on prayers and tasks
- **Streak System** — Tracks consecutive days of discipline
- **Dashboard** — Central overview of your entire day at a glance
- **Admin Panel** — Full Django admin access for all models

---

## Tech Stack

| Layer    | Technology           |
|----------|----------------------|
| Backend  | Django 5.0           |
| Database | SQLite (development) |
| Frontend | Django Templates     |
| Styling  | Custom CSS           |
| Auth     | Django built-in auth |

---

## Project Structure

```
deen_discipline_os/
├── core/                   # Main app (models, views, forms, urls, admin)
├── templates/              # All HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── 404.html
│   ├── 500.html
│   ├── tasks/
│   ├── prayers/
│   ├── journal/
│   └── registration/
├── static/
│   └── css/style.css
├── deen_discipline_os/     # Project settings and root URLs
└── manage.py
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd deen_discipline_os
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (for admin access)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

---

## Discipline Score Formula

| Action                | Points       |
|-----------------------|--------------|
| Each prayer completed | +10 (max 50) |
| Each prayer on time   | +5  (max 25) |
| Task completion ratio | up to 25     |
| **Total**             | **100**      |

---

## Future Improvements

- PostgreSQL support for production deployment
- Weekly and monthly performance history graphs
- Prayer time reminders and Qibla direction
- Dark mode toggle
- Mobile PWA support
- Export journal entries as PDF
- Long-term goal tracking system
- Email notifications for daily summaries
