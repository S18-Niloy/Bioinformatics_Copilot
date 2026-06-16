# Security Guidelines

## Overview
This document outlines the security measures implemented in the Bioinformatics Copilot application.

---

## 🔐 Authentication & Authorization

### JWT Tokens
- **Access Tokens**: 15-minute expiration (short-lived)
- **Refresh Tokens**: 7-day expiration (for token renewal)
- **Token Type Validation**: Tokens are marked with type (`access` or `refresh`) to prevent misuse
- **Secret Key**: Minimum 32 characters; must be set via `JWT_SECRET` environment variable

### Password Security
- **Hashing Algorithm**: Argon2 (via passlib)
- **Minimum Length**: 8 characters
- **Maximum Length**: 72 bytes (bcrypt limit)
- **Strength Requirements**:
  - At least one uppercase letter
  - At least one digit
  - At least one special character (!@#$%^&*)

### User Validation
- **Username**: 3-50 characters, alphanumeric + underscore/hyphen only
- **Account Status**: Users can be marked inactive

---

## 🛡️ API Security

### CORS (Cross-Origin Resource Sharing)
- **Configuration**: Only specific origins allowed (whitelist-based)
- **Default**: `http://localhost:3000` for development
- **Production**: Set `ALLOWED_ORIGINS` environment variable
- **Methods**: Only `GET` and `POST` allowed
- **Headers**: Restricted to `Content-Type` and `Authorization`

### Trusted Host Validation
- **Configuration**: `ALLOWED_HOSTS` environment variable (comma-separated)
- **Default**: `localhost,127.0.0.1`
- **Production**: Must include your domain

### Error Handling
- **Stack Traces**: Not leaked to clients in production
- **Generic Errors**: Clients receive generic "Internal server error" messages
- **Logging**: Full error details logged server-side for debugging

### Input Validation
- **Pydantic Models**: All inputs validated with Pydantic
- **Type Checking**: Strict type enforcement
- **Length Limits**: Enforced on all string fields
- **Character Validation**: Sequences validated for valid bioinformatics characters

---

## 🗄️ Database Security

### SQL Injection Prevention
- **ORM Usage**: SQLAlchemy ORM prevents SQL injection
- **Parameterized Queries**: All queries use parameterized statements
- **Input Validation**: User inputs validated before database operations

### Connection Management
- **Connection Pooling**: Configured for production databases
- **Connection Testing**: `pool_pre_ping=True` ensures connections are live before use
- **Foreign Keys**: Enabled for referential integrity (SQLite)

### Database Selection
- **Development**: SQLite (convenient, secure enough for dev)
- **Production**: PostgreSQL or MySQL recommended
- **Configuration**: Set `DATABASE_URL` environment variable

---

## 🔑 Secrets Management

### Environment Variables
All sensitive configuration must be set via environment variables:

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `JWT_SECRET` | JWT signing key | Yes (prod) | dev-generated |
| `DATABASE_URL` | Database connection | No | `sqlite:///./biocopilot.db` |
| `ALLOWED_ORIGINS` | CORS origins | No | `http://localhost:3000` |
| `ALLOWED_HOSTS` | Trusted hosts | No | `localhost,127.0.0.1` |
| `ENVIRONMENT` | Deployment environment | No | `development` |

### .env File
- **Location**: `/backend/.env`
- **Never Commit**: Add `.env` to `.gitignore`
- **Template**: Use `.env.example` as template
- **Generation**: Use `python -c "import secrets; print(secrets.token_urlsafe(32))"` for secure keys

---

## 🐳 Docker Security

### Image Security
- **Base Image**: `python:3.11-slim` (minimal attack surface)
- **Package Cleanup**: APT cache cleared after installation
- **Non-Root User**: Recommended in production (not currently enforced)

### Environment Configuration
- **No Hardcoded Secrets**: All secrets passed at runtime
- **Compose Override**: Use `docker-compose.override.yml` for local overrides

---

## 📝 Logging & Monitoring

### What Gets Logged
- ✅ Authentication events (login, registration, token refresh)
- ✅ API errors (type and context, not sensitive data)
- ✅ Database errors
- ✅ Unhandled exceptions

### What Doesn't Get Logged
- ❌ Passwords or password hashes
- ❌ Tokens or JWT secrets
- ❌ User input details (only validation summaries)
- ❌ Full stack traces in production

### Log Levels
- `DEBUG`: Detailed information for development
- `INFO`: General informational messages
- `WARNING`: Warning messages for issues
- `ERROR`: Error events requiring attention
- `CRITICAL`: Critical events

---

## 🚀 Production Deployment

### Prerequisites
1. Set `ENVIRONMENT=production`
2. Generate strong `JWT_SECRET` (minimum 32 characters)
3. Configure `ALLOWED_ORIGINS` for your frontend domain
4. Configure `ALLOWED_HOSTS` for your API domain
5. Use PostgreSQL or MySQL instead of SQLite
6. Enable HTTPS/TLS at reverse proxy level

### Dockerfile Improvements
```bash
# Build minimal image
docker build -t bioinformatics-copilot-backend:latest -f Dockerfile.backend .

# Run with security settings
docker run \
  --env ENVIRONMENT=production \
  --env JWT_SECRET=<strong-secret> \
  --env DATABASE_URL=postgresql://... \
  --env ALLOWED_ORIGINS=https://yourdomain.com \
  --env ALLOWED_HOSTS=api.yourdomain.com \
  -p 8000:8000 \
  bioinformatics-copilot-backend:latest
```

### Reverse Proxy Configuration
- **HTTPS/TLS**: Configure at reverse proxy (nginx, Traefik)
- **Security Headers**: Add HSTS, CSP headers at reverse proxy
- **Rate Limiting**: Implement at reverse proxy level
- **DDoS Protection**: Consider Cloudflare or similar

### Database Security
- **Backups**: Regular automated backups
- **Encryption**: Enable database encryption at rest
- **Access Control**: Restrict database access by IP
- **Audit Logging**: Enable if supported by database

---

## 🔍 Security Checklist

### Before Production Deployment
- [ ] JWT_SECRET is strong (minimum 32 characters) and unique
- [ ] ALLOWED_ORIGINS configured for your domain
- [ ] ALLOWED_HOSTS configured for your domain
- [ ] ENVIRONMENT set to `production`
- [ ] Using PostgreSQL or MySQL (not SQLite)
- [ ] HTTPS/TLS enabled at reverse proxy
- [ ] Logging configured appropriately
- [ ] Database backups configured
- [ ] Rate limiting implemented (at reverse proxy)
- [ ] Secrets not committed to version control
- [ ] `.env` added to `.gitignore`

### Regular Maintenance
- [ ] Monthly: Review and rotate JWT_SECRET
- [ ] Quarterly: Update dependencies for security patches
- [ ] Quarterly: Review access logs for suspicious activity
- [ ] Annually: Security audit and penetration testing

---

## 🐛 Reporting Security Issues

If you discover a security vulnerability, please email security@example.com (update with your contact).
Do not open public GitHub issues for security vulnerabilities.

---

## References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/faq/security.html)
- [Argon2 Password Hashing](https://github.com/hynek/argon2-cffi)
