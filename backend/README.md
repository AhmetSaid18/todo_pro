# 🎬 TODO Production Management System - Backend

Django-based backend for production management in film/video industry.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Development Setup

1. **Clone and navigate**
```bash
cd backend
```

2. **Configure environment**
```bash
# .env dosyası zaten hazır, gerekirse düzenle
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Run migrations**
```bash
docker-compose exec web python manage.py migrate
```

5. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Access the API**
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/schema/swagger/

## 📦 Services

- **web**: Django + Daphne (ASGI)
- **db**: PostgreSQL 15
- **redis**: Redis 7
- **celery**: Celery Worker
- **celery-beat**: Celery Scheduler

## 🛠️ Development Commands

### Django Management
```bash
# Make migrations
docker-compose exec web python manage.py makemigrations

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Shell
docker-compose exec web python manage.py shell

# Collect static files
docker-compose exec web python manage.py collectstatic
```

### Docker Commands
```bash
# View logs
docker-compose logs -f web

# Restart service
docker-compose restart web

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 🏗️ Project Structure

```
backend/
├── api/                    # Main API app
│   ├── models/            # Database models
│   ├── serializers/       # DRF serializers
│   ├── views/             # API views
│   ├── permissions.py     # Custom permissions
│   └── signals.py         # Django signals
├── apps/
│   ├── core/              # Core utilities
│   ├── users/             # User management
│   ├── agencies/          # Multi-tenant (Agency)
│   ├── projects/          # Project management
│   ├── tasks/             # Task management
│   └── equipment/         # Equipment inventory
├── config/                # Django settings
│   ├── settings.py        # Main settings
│   ├── urls.py            # Root URLs
│   ├── asgi.py            # ASGI config
│   └── celery.py          # Celery config
└── docker-compose.yml     # Docker setup
```

## 🔐 Environment Variables

Key variables in `.env`:

```bash
DEBUG=True                              # Set to False in production
DJANGO_SECRET_KEY=change-me             # Generate new secret key
ALLOWED_HOSTS=localhost,yourdomain.com  # Add your domain
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 📡 API Endpoints

### Authentication
- POST `/api/auth/register/` - Register
- POST `/api/auth/login/` - Login (JWT)
- POST `/api/auth/refresh/` - Refresh token

### Core Resources
- `/api/projects/` - Projects
- `/api/tasks/` - Tasks
- `/api/items/` - Equipment
- `/api/reservations/` - Equipment reservations
- `/api/users/` - Users
- `/api/clients/` - Clients

### System
- `/api/health/` - Health check (no auth)

## 🧪 Testing

```bash
# Run tests
docker-compose exec web python manage.py test

# With coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## 📊 Database Management

### Backup
```bash
docker-compose exec db pg_dump -U todopro_user todopro_db > backup.sql
```

### Restore
```bash
cat backup.sql | docker-compose exec -T db psql -U todopro_user todopro_db
```

## 🔥 Production Deployment

### 1. Update .env for production
```bash
DEBUG=False
DJANGO_SECRET_KEY=<generate-strong-secret>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. Run with production settings
```bash
docker-compose up -d
```

### 3. Collect static files
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Setup Nginx (on server)
Point to port 8000 for backend, serve static/media files

## 📝 Notes

- **Multi-tenancy**: Agency-based isolation (her firma kendi datasını görür)
- **WebSocket**: Django Channels ile real-time notifications
- **Task Queue**: Celery ile async job processing
- **API Docs**: Swagger UI otomatik oluşturulur

## 🤝 Team

Built with ❤️ for production companies

---
**Status**: Development  
**Last Updated**: 2026-01-18
