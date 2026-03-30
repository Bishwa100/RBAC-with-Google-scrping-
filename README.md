# TopicLens - Unified RBAC + Content Analysis Platform

A comprehensive content analysis and web scraping platform with role-based access control (RBAC). Built with FastAPI, React, and modern web technologies.

---

## 🏗️ Architecture

**Unified Backend Architecture:**
- Single FastAPI backend (port 8000)
- RBAC authentication & authorization
- TopicLens content analysis features (root user only)
- PostgreSQL for data persistence
- Redis + Celery for background jobs

**Services:**
1. **Backend** (port 8000) - Unified RBAC + TopicLens API
2. **Frontend** (port 3000) - React SPA with TailwindCSS
3. **PostgreSQL** (port 5432) - Database
4. **Redis** (port 6379) - Job queue & cache
5. **PgAdmin** (port 5050) - Database management UI
6. **Celery Worker** - Background job processing
7. **Doc Extractor** (port 8001) - Document processing service

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Or: Node.js 18+, Python 3.11+, PostgreSQL, Redis

### Start with Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Access the Application

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | - |
| **Backend API** | http://localhost:8000/docs | - |
| **PgAdmin** | http://localhost:5050 | admin@admin.com / admin |

**Login (Root User):**
- Email: `admin@topiclens.com`
- Password: `AdminPass123!`

---

## 📚 Features

### RBAC Features (All Users)
✅ User authentication with JWT  
✅ Role-based access control  
✅ User management  
✅ Department management  
✅ Permission scopes  
✅ Audit logging  
✅ Document processing  

### TopicLens Features (Root User Only)
🔒 Multi-source web scraping (10+ sources)  
🔒 AI-powered content analysis  
🔒 Deep LLM analysis  
🔒 Background job processing  
🔒 Real-time status tracking  

**Available Sources:**
- GitHub, Reddit, YouTube
- Twitter, LinkedIn, Facebook
- Instagram, Quora, Blogs
- Events and more

---

## 🔐 Security & Permissions

### TopicLens Access Control

TopicLens features are **protected** and require the `topiclens:access` permission:

- **Granted to**: Root role only (by default)
- **Endpoints**: `/api/v1/topiclens/*`
- **Protection**: All endpoints check user permissions

**Non-root users** attempting to access TopicLens features will receive:
```json
{
  "error": "forbidden",
  "detail": "Missing required scope: topiclens:access",
  "status_code": 403
}
```

---

## 📝 API Documentation

### Authentication & RBAC

Base URL: `http://localhost:8000/api/v1`

**Endpoints:**
- `POST /auth/login` - Login with email/password
- `POST /auth/logout` - Logout
- `POST /auth/refresh` - Refresh access token
- `GET /users` - List users
- `POST /users` - Create user
- `GET /roles` - List roles
- `GET /departments` - List departments
- `GET /audit` - Audit logs

### TopicLens (Root Only)

Base URL: `http://localhost:8000/api/v1/topiclens`

**Endpoints:**
- `POST /search` - Start topic search job
- `GET /status/{job_id}` - Get job status
- `POST /analyze` - Analyze URL content
- `GET /sources` - List available sources
- `GET /jobs` - List all jobs
- `GET /health` - Health check

**Example: Start a search**
```bash
curl -X POST http://localhost:8000/api/v1/topiclens/search \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Artificial Intelligence",
    "sources": ["github", "reddit", "youtube"],
    "deep_analysis": true
  }'
```

---

## 🛠️ Development

### Local Development Setup

**Backend:**
```bash
cd RBAC-main/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python create_topiclens_permissions.py
uvicorn main:app --reload
```

**Worker:**
```bash
cd RBAC-main/backend
celery -A app.topiclens.celery_app worker --loglevel=info
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

**Backend (`.env` in `RBAC-main/backend/`):**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/rbac_db
SECRET_KEY=your-secret-key-here
ROOT_EMAIL=admin@topiclens.com
ROOT_PASSWORD=AdminPass123!

# TopicLens
TOPICLENS_REDIS_URL=redis://localhost:6379/0
TOPICLENS_HF_MODEL_ID=microsoft/phi-2
TOPICLENS_HF_DEVICE=cpu
TOPICLENS_CELERY_BROKER_URL=redis://localhost:6379/0
```

**Frontend (`.env` in `frontend/`):**
```env
VITE_API_URL=http://localhost:8000
```

---

## 📦 Project Structure

```
topicLens/
├── RBAC-main/
│   ├── backend/                    # Unified Backend
│   │   ├── app/
│   │   │   ├── api/v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── roles.py
│   │   │   │   └── topiclens.py   # TopicLens endpoints
│   │   │   ├── topiclens/          # TopicLens modules
│   │   │   │   ├── scrapers/
│   │   │   │   ├── analyzers/
│   │   │   │   ├── llm.py
│   │   │   │   ├── tasks.py
│   │   │   │   └── celery_app.py
│   │   │   ├── models/
│   │   │   │   ├── all.py
│   │   │   │   └── topiclens.py   # Job models
│   │   │   ├── core/
│   │   │   └── db/
│   │   ├── migrations/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── create_topiclens_permissions.py
│   └── doc_extractor/
│
├── frontend/                       # React Frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts          # Unified API client
│   │   ├── pages/
│   │   ├── components/
│   │   └── store/
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml              # All services
└── OPTIMIZATION_COMPLETE.md        # Optimization details
```

---

## 🧪 Testing

### Test Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@topiclens.com","password":"AdminPass123!"}'
```

### Test TopicLens (Root User)
```bash
# Should succeed for root user
curl -X GET http://localhost:8000/api/v1/topiclens/sources \
  -H "Authorization: Bearer <root_token>"

# Should fail (403) for non-root user
curl -X GET http://localhost:8000/api/v1/topiclens/sources \
  -H "Authorization: Bearer <regular_user_token>"
```

---

## 🔄 Database Migrations

```bash
cd RBAC-main/backend

# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs backend
docker-compose logs worker

# Restart services
docker-compose restart
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Permission errors for TopicLens
```bash
# Recreate permissions
docker-compose exec backend python create_topiclens_permissions.py
```

---

## 📖 Documentation

- **OPTIMIZATION_COMPLETE.md** - Optimization process details
- **API Documentation** - http://localhost:8000/docs (when running)
- **Database Schema** - See migrations in `RBAC-main/backend/migrations/`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📄 License

[Add your license here]

---

## 🆘 Support

For issues and questions:
- Check the documentation
- Review API docs at `/docs`
- Check docker logs for errors

---

## 🎯 Roadmap

- [ ] Add TopicLens UI pages to frontend
- [ ] Implement advanced search filters
- [ ] Add export functionality for results
- [ ] Support for custom data sources
- [ ] Enhanced analytics dashboard

---

**Built with ❤️ using FastAPI, React, PostgreSQL, and modern web technologies**
