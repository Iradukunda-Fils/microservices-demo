# Security Overview

## Introduction

This document provides a high-level overview of security measures implemented in the Microservices Demo project.

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Security Layers                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Network Security                                             │
│     ├─ HTTPS/TLS (Production)                                   │
│     ├─ Network Segmentation (Docker networks)                   │
│     └─ API Gateway (Single entry point)                         │
│                                                                  │
│  2. Authentication & Authorization                               │
│     ├─ JWT with RS256 (RSA signatures)                          │
│     ├─ Two-Factor Authentication (TOTP)                         │
│     ├─ Password Hashing (PBKDF2-SHA256)                         │
│     └─ Service-to-Service Auth (Shared secret / mTLS)           │
│                                                                  │
│  3. Data Protection                                              │
│     ├─ Field-Level Encryption (AES-256)                         │
│     ├─ Encrypted Backup Tokens (PBKDF2-SHA256)                  │
│     └─ Secure Cookie Storage (httpOnly, secure, samesite)       │
│                                                                  │
│  4. Application Security                                         │
│     ├─ Input Validation                                         │
│     ├─ SQL Injection Prevention (ORM)                           │
│     ├─ XSS Prevention (React escaping)                          │
│     └─ CSRF Protection (SameSite cookies)                       │
│                                                                  │
│  5. Resilience & Monitoring                                      │
│     ├─ Circuit Breakers                                         │
│     ├─ Retry Logic                                              │
│     ├─ Rate Limiting                                            │
│     └─ Comprehensive Logging                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Security Features

### 1. JWT Authentication with RS256

**Pattern**: Identity Provider (IdP)

- **UserService** acts as Identity Provider
  - Owns RSA private key (4096-bit)
  - Signs JWT tokens
  - Distributes public key to services

- **Other Services** verify tokens locally
  - Use public key for verification
  - No network calls to UserService
  - 50% latency reduction

**Benefits**:
- Centralized authentication
- Distributed authorization
- Scalable architecture
- Industry standard (OAuth 2.0, OpenID Connect)

**Documentation**: [JWT Best Practices](JWT_BEST_PRACTICES.md)

### 2. Two-Factor Authentication (2FA)

**Implementation**: TOTP (Time-based One-Time Password)

- Compatible with Google Authenticator, Authy, Microsoft Authenticator
- 6-digit codes that change every 30 seconds
- 10 backup tokens for account recovery
- Hashed token storage (PBKDF2-SHA256)
- One-time use enforcement

**Benefits**:
- Protects against password theft
- More secure than SMS-based 2FA
- Industry standard (NIST recommended)

**Documentation**: [Two-Factor Authentication](../features/TWO_FACTOR_AUTH.md)

### 3. gRPC Security

**Current**: Shared secret authentication (Development)

**Recommended**: Mutual TLS (mTLS) for production

- Both client and server authenticate
- All traffic encrypted (TLS 1.3)
- Certificate-based access control
- Industry standard for service-to-service communication

**Documentation**: [gRPC Security](GRPC_SECURITY.md)

### 4. Data Encryption

**At Rest**:
- Field-level encryption (AES-256)
- Encrypted sensitive fields (user_id in orders)
- Hashed passwords (PBKDF2-SHA256)
- Hashed backup tokens (PBKDF2-SHA256)

**In Transit**:
- HTTPS/TLS for external communication (Production)
- gRPC with mTLS for internal communication (Recommended)

**Documentation**: [Data Protection](DATA_PROTECTION.md)

### 5. Resilience Patterns

**Circuit Breaker**:
- Prevents cascading failures
- Fails fast when service is down
- Automatic recovery testing

**Retry Logic**:
- Exponential backoff
- Handles transient failures
- Configurable attempts and delays

**Documentation**: [Resilience Patterns](../patterns/RESILIENCE_PATTERNS.md)

## Security by Service

### UserService (Identity Provider)

**Responsibilities**:
- User authentication
- JWT token generation
- 2FA management
- Public key distribution

**Security Measures**:
- RSA private key (4096-bit) - never shared
- Password hashing (PBKDF2-SHA256)
- TOTP secret encryption
- Backup token hashing
- Rate limiting on login attempts
- Audit logging

**Endpoints**:
- `POST /api/token/` - Login (rate limited)
- `POST /api/token/refresh/` - Token refresh
- `GET /api/auth/public-key/` - Public key (cached)
- `POST /api/users/2fa/setup/` - 2FA setup (authenticated)
- `POST /api/users/2fa/verify-login/` - 2FA verification

### ProductService

**Responsibilities**:
- Product catalog
- Inventory management

**Security Measures**:
- JWT verification with public key
- No direct database access from other services
- gRPC authentication (shared secret / mTLS)
- Input validation
- Audit logging

**Endpoints**:
- `GET /api/products/` - List products (authenticated)
- `POST /api/products/` - Create product (admin only)
- gRPC: `GetProductInfo`, `CheckAvailability`

### OrderService

**Responsibilities**:
- Order creation
- Cross-service validation

**Security Measures**:
- JWT verification with public key
- Field-level encryption (user_id)
- gRPC client authentication
- Circuit breakers for resilience
- Retry logic with exponential backoff
- Input validation
- Audit logging

**Endpoints**:
- `POST /api/orders/` - Create order (authenticated)
- `GET /api/orders/{id}/` - Get order (owner or admin)
- `GET /api/orders/user/{user_id}/` - User orders (owner or admin)

### Frontend

**Responsibilities**:
- User interface
- Token management

**Security Measures**:
- Secure cookie storage (httpOnly, secure, samesite)
- Automatic token refresh
- XSS prevention (React escaping)
- CSRF protection (SameSite cookies)
- Input validation
- No sensitive data in localStorage

## Threat Model

### External Threats

**1. Unauthorized Access**
- **Threat**: Attacker tries to access protected resources
- **Mitigation**: JWT authentication, 2FA, rate limiting

**2. Token Theft**
- **Threat**: Attacker steals JWT token
- **Mitigation**: Short expiration (15 min), httpOnly cookies, HTTPS

**3. Brute Force Attacks**
- **Threat**: Attacker tries many passwords
- **Mitigation**: Rate limiting, account lockout, 2FA

**4. Man-in-the-Middle (MITM)**
- **Threat**: Attacker intercepts communication
- **Mitigation**: HTTPS/TLS, certificate pinning

**5. SQL Injection**
- **Threat**: Attacker injects malicious SQL
- **Mitigation**: ORM (Django), parameterized queries

**6. Cross-Site Scripting (XSS)**
- **Threat**: Attacker injects malicious JavaScript
- **Mitigation**: React escaping, Content Security Policy

**7. Cross-Site Request Forgery (CSRF)**
- **Threat**: Attacker tricks user into making requests
- **Mitigation**: SameSite cookies, CSRF tokens

### Internal Threats

**1. Service Impersonation**
- **Threat**: Malicious service pretends to be legitimate
- **Mitigation**: mTLS, service authentication

**2. Data Breach**
- **Threat**: Database compromised
- **Mitigation**: Field-level encryption, hashed passwords

**3. Privilege Escalation**
- **Threat**: User gains unauthorized permissions
- **Mitigation**: Role-based access control, JWT claims validation

**4. Denial of Service (DoS)**
- **Threat**: Attacker overwhelms service
- **Mitigation**: Rate limiting, circuit breakers, timeouts

## Security Checklist

### Development ✅
- [x] JWT with RS256
- [x] Password hashing (PBKDF2-SHA256)
- [x] Two-factor authentication (TOTP)
- [x] Field-level encryption (AES-256)
- [x] Input validation
- [x] SQL injection prevention (ORM)
- [x] XSS prevention (React)
- [x] CSRF protection (SameSite)
- [x] Circuit breakers
- [x] Retry logic
- [x] Audit logging

### Production ⚠️
- [ ] **HTTPS/TLS** (TLS 1.3)
- [ ] **mTLS for gRPC** (mutual authentication)
- [ ] **Certificate management** (rotation, monitoring)
- [ ] **Secrets management** (Vault, AWS Secrets Manager)
- [ ] **Rate limiting** (API Gateway)
- [ ] **WAF** (Web Application Firewall)
- [ ] **DDoS protection** (Cloudflare, AWS Shield)
- [ ] **Security headers** (CSP, HSTS, X-Frame-Options)
- [ ] **Vulnerability scanning** (OWASP ZAP, Snyk)
- [ ] **Penetration testing** (annual)
- [ ] **Security monitoring** (SIEM, alerts)
- [ ] **Incident response plan**
- [ ] **Backup and recovery** (encrypted backups)
- [ ] **Compliance** (GDPR, SOC 2, PCI-DSS)

## Security Testing

### Manual Testing

**Authentication**:
```bash
# Test login
curl -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test with invalid credentials
curl -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "wrong"}'

# Test token verification
curl -H "Authorization: Bearer INVALID_TOKEN" \
  http://localhost/api/products/
```

**2FA**:
```bash
# Test 2FA setup
curl -X POST http://localhost/api/users/2fa/setup/ \
  -H "Authorization: Bearer TOKEN"

# Test 2FA verification
curl -X POST http://localhost/api/users/2fa/verify-login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "token": "123456"}'
```

### Automated Testing

**Unit Tests**:
```python
# Test JWT verification
def test_jwt_verification():
    token = generate_token(user)
    payload = verify_token(token)
    assert payload['user_id'] == user.id

# Test 2FA
def test_2fa_verification():
    device = setup_2fa(user)
    code = device.generate_code()
    assert verify_2fa(user, code) == True
```

**Integration Tests**:
```python
# Test authentication flow
def test_login_flow():
    response = client.post('/api/token/', {
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 200
    assert 'access' in response.json()
```

**Security Tests**:
```python
# Test SQL injection prevention
def test_sql_injection():
    response = client.get('/api/products/?search=\' OR 1=1--')
    assert response.status_code == 200
    # Should not return all products

# Test XSS prevention
def test_xss_prevention():
    response = client.post('/api/products/', {
        'name': '<script>alert("XSS")</script>'
    })
    # Should escape script tags
```

## Incident Response

### Detection

**Monitoring**:
- Failed login attempts (> 5 in 5 minutes)
- Invalid JWT tokens (> 10 in 1 minute)
- Unusual API usage patterns
- Service errors (> 5% error rate)
- Circuit breaker openings

**Alerts**:
- Email notifications
- Slack/PagerDuty integration
- SMS for critical incidents

### Response

**1. Identify**:
- What happened?
- When did it happen?
- What systems are affected?

**2. Contain**:
- Isolate affected systems
- Revoke compromised tokens
- Block malicious IPs
- Enable additional logging

**3. Eradicate**:
- Remove malicious code
- Patch vulnerabilities
- Rotate compromised credentials
- Update security rules

**4. Recover**:
- Restore from backups
- Verify system integrity
- Monitor for recurrence
- Gradual service restoration

**5. Learn**:
- Post-mortem analysis
- Update security measures
- Improve monitoring
- Train team

## Compliance

### GDPR (General Data Protection Regulation)

- **Right to Access**: Users can request their data
- **Right to Erasure**: Users can delete their account
- **Data Minimization**: Only collect necessary data
- **Encryption**: Sensitive data encrypted
- **Audit Logging**: Track data access

### SOC 2 (Service Organization Control 2)

- **Security**: Access controls, encryption
- **Availability**: High availability, backups
- **Processing Integrity**: Data validation
- **Confidentiality**: Data protection
- **Privacy**: GDPR compliance

### PCI-DSS (Payment Card Industry Data Security Standard)

- **Not Applicable**: No payment card data stored
- **If Implemented**: Use payment gateway (Stripe, PayPal)

## Further Reading

- [JWT Best Practices](JWT_BEST_PRACTICES.md)
- [gRPC Security](GRPC_SECURITY.md)
- [Data Protection](DATA_PROTECTION.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls/)

---

**Last Updated**: 2026-01-01
**Security Level**: Development (requires production hardening)
