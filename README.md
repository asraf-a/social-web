# 📌 Bookmarks — Social Image Bookmarking Platform

A modern, Pinterest-like social media web application built with **Django 6**, **Python 3.14**, **Redis**, and **Google OAuth 2.0**.

---

## ✨ Features

- 🔐 **Authentication & Profiles**:
  - Email or Username login with custom authentication backends.
  - **Google OAuth 2.0** Single Sign-On.
  - User profiles with avatars and birthdates.
  - Secure password reset via email.
- 🔖 **Browser Bookmarklet Tool**:
  - Drag-and-drop JavaScript bookmarklet to scan and bookmark images from any website on the internet.
  - Automatic download and processing with `requests` and `Pillow`.
  - Dynamic smart thumbnails powered by `easy-thumbnails`.
- ❤️ **Interactive Interactions**:
  - Instant AJAX like/unlike toggle.
  - Infinite scroll gallery with AJAX pagination.
- 👥 **Follow System & Activity Feed**:
  - Follow and unfollow members with real-time stats.
  - User directory (`/account/users/`) and user detail profiles.
  - Generic relation activity stream (`actions` app) with 60-second duplicate throttling.
  - Follower activity stream on the user dashboard.
- ⚡ **Real-time Leaderboard & Signals**:
  - View counters and sorted set ranking powered by **Redis** (with `fakeredis` high-performance in-memory fallback).
  - Denormalized `total_likes` kept in sync automatically via Django signals.
  - Top 10 most viewed images leaderboard (`/images/ranking/`).

---

## 🛠️ Tech Stack

- **Backend**: Python 3.14, Django 6.1.1, SQLite3, Redis / FakeRedis
- **Frontend**: HTML5, CSS3, JavaScript (ES6), jQuery 3.7.1
- **Auth**: Google OAuth 2.0 via `social-auth-app-django`
- **Media**: Pillow, easy-thumbnails

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Set up virtual environment
```bash
python -m venv env
# On Windows:
.\env\Scripts\activate
# On macOS/Linux:
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r bookmarks/requirements.txt
```

### 4. Apply migrations
```bash
cd bookmarks
python manage.py migrate
```

### 5. Run tests
```bash
python manage.py test
```

### 6. Start the server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
