# Security Policy — Infinity Template Library

## Reporting Vulnerabilities

Report security vulnerabilities to: security@infinityxai.com

Do **not** open public GitHub issues for security vulnerabilities.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes     |
| < 1.0   | ❌ No      |

## Security Architecture

### Authentication
- All API templates use JWT (HS256) with configurable expiry
- Passwords hashed with bcrypt (cost factor 12)
- Refresh token rotation supported

### Transport Security
- All templates enforce HTTPS in production
- CORS origins must be explicitly allowlisted
- HSTS headers via helmet (Express) / FastAPI middleware

### Secrets Management
- All secrets loaded via environment variables (never hardcoded)
- `.env` files are gitignored
- GitHub Actions Secrets used for CI/CD

### Dependency Security
- Weekly automated dependency audits via pip-audit and npm audit
- SAST scanning via CodeQL
- Secret scanning via TruffleHog

### AI Agent Safety
- Safety guardrails block harmful query patterns
- Tool calls are audited in AgentMemory
- LLM inputs/outputs logged for review

### Container Security
- Containers run as non-root user
- Minimal base images (python:3.12-slim, node:20-alpine)
- Read-only file systems where possible

## Security Checklist for Generated Systems

- [ ] Rotate SECRET_KEY before deployment
- [ ] Set ENV=production
- [ ] Configure explicit CORS_ORIGINS
- [ ] Enable database encryption at rest
- [ ] Configure HTTPS/TLS termination
- [ ] Enable audit logging
- [ ] Review and restrict IAM permissions
