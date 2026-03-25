# Invoice Gem Backend — Deployment Guide

This Django backend handles Pro license verification and secure cloud backups for the Invoice Gem Flutter app.

---

## 🛠️ Prerequisites
- Python 3.10+
- PostgreSQL (Recommended for production)
- Nginx + Gunicorn (For VPS deployment)

## 📦 Installation

1. **Clone & Setup Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   Create a `.env` file in the `backend/` root:
   ```env
   DEBUG=False
   SECRET_KEY=your_very_secret_key_here
   ALLOWED_HOSTS=yourdomain.com,your_vps_ip
   PAYSTACK_SECRET_KEY=sk_live_xxxx
   PRO_PRICE_KOBO=500000  # e.g., 5000.00 in minor units
   ```

3. **Database & Migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # To access /admin
   ```

4. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

## 🚀 VPS Deployment (Nginx + Gunicorn)

### Gunicorn Configuration
Run Gunicorn to serve the Django app:
```bash
gunicorn --workers 3 --bind 0.0.0.0:8000 invoice_gem_backend.wsgi:application
```

### Nginx Configuration
Create a site configuration (e.g., `/etc/nginx/sites-available/invoice_gem`):
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/your/backend/static/;
    }
}
```

## 🔒 Security Notes
- **CORS**: In `settings.py`, restrict `CORS_ALLOW_ALL_ORIGINS` to your specific domain in production.
- **SSL**: Always use HTTPS (via Certbot/Let's Encrypt) to protect JWT tokens and backup data.
- **Backups**: The `backups` app uses local storage by default. For production, consider configuring Django to use AWS S3 or similar.

---
**Invoice Gem Backend is now ready to support your global user base.**
