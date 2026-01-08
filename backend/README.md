---
title: Hackathon 2 - Task Manager API
emoji: ☕
colorFrom: brown
colorTo: yellow
sdk: docker
pinned: false
license: mit
---

# ActionMind AI - Task Manager API

FastAPI backend for task management with JWT authentication.

## 🚀 Features

- **User Authentication**: Register & Login with JWT tokens
- **Task Management**: Create, Read, Update, Delete tasks
- **SQLite Database**: Lightweight and portable
- **RESTful API**: Clean and documented endpoints
- **CORS Enabled**: Ready for frontend integration

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/token` - Login & get JWT token

### Tasks
- `GET /api/tasks` - Get all tasks (requires auth)
- `POST /api/tasks` - Create new task (requires auth)
- `PUT /api/tasks/{id}` - Update task (requires auth)
- `DELETE /api/tasks/{id}` - Delete task (requires auth)

## 📚 API Documentation

Visit `/docs` for interactive Swagger API documentation.

## 🔧 Environment Variables (Optional)

The API uses default settings, but you can override:
- `SECRET_KEY`: JWT secret key (default: auto-generated)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiry in minutes (default: 30)
- `DATABASE_URL`: SQLite database path (default: sqlite:///./hackathon_tasks.db)

## 🔗 Frontend Integration

Add this URL to your frontend environment variables:
```
https://duaapirzada-hackathon-2.hf.space
```

## 📝 Example Usage

### Register User
```bash
curl -X POST "https://duaapirzada-hackathon-2.hf.space/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

### Login
```bash
curl -X POST "https://duaapirzada-hackathon-2.hf.space/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### Create Task (with token)
```bash
curl -X POST "https://duaapirzada-hackathon-2.hf.space/api/tasks" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Task", "description": "Task description", "priority": "high"}'
```
