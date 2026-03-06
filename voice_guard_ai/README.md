# 🛡️ VOICE_GUARD_AI
### AI Based Voice Impersonation Detection System
**Final Year Project | Django + Machine Learning**

---

## 🚀 Setup Instructions

### 1. Clone / Extract the project
```bash
cd voice_guard_ai
```

### 2. Create & activate virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** `librosa` is required for real audio analysis.
> If it fails to install, the system falls back to simulation mode (still demonstrates all features).

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create admin superuser
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

### 7. Open in browser
```
http://127.0.0.1:8000/
```

---

## 📁 Project Structure

```
voice_guard_ai/
├── voice_guard_ai/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                    # Main application
│   ├── templates/core/      # HTML templates
│   │   ├── base.html        # Base layout with navbar
│   │   ├── index.html       # Landing page
│   │   ├── login.html       # Login page
│   │   ├── signup.html      # Registration page
│   │   ├── dashboard.html   # Main dashboard
│   │   ├── history.html     # Analysis history
│   │   └── analysis_detail.html  # Detailed result view
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── urls.py              # URL routing
│   ├── forms.py             # Django forms
│   ├── detector.py          # 🧠 AI Detection Engine
│   └── admin.py             # Admin configuration
├── media/                   # Uploaded audio files
├── requirements.txt
└── manage.py
```

---

## 🧠 Detection Features

The system analyzes 5 key audio features:

| Feature | What It Detects |
|---------|----------------|
| **Spectral Analysis** | Frequency distribution patterns unique to human vs synthetic voice |
| **Pitch Detection** | Natural pitch variation (humans vary, AI is too regular) |
| **Rhythm Analysis** | Speech timing patterns and beat regularity |
| **Noise Fingerprint** | Background noise and acoustic signatures |
| **Formant Profiling** | MFCC-based vocal tract resonance characteristics |

---

## 📊 Pages

| URL | Description |
|-----|-------------|
| `/` | Landing page with features & CTA |
| `/signup/` | User registration |
| `/login/` | User login |
| `/dashboard/` | Main dashboard with upload, stats, charts |
| `/history/` | All past analyses with filters |
| `/analysis/<id>/` | Detailed result for a single analysis |
| `/admin/` | Django admin panel |

---

## 🔧 Admin Access
Visit `http://127.0.0.1:8000/admin/` with your superuser credentials to manage users and analyses.

---

*Built with Django, Librosa, Chart.js | Final Year Project 2024*
