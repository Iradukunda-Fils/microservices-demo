# Contributing to Microservices Demo

Thank you for your interest in contributing! This is an educational project designed to help developers learn microservices architecture. We welcome contributions from the community.

## 🎯 Ways to Contribute

1. **Report Bugs** - Found a bug? Open an issue with details
2. **Suggest Features** - Have an idea? Share it in discussions
3. **Improve Documentation** - Help make docs clearer
4. **Submit Code** - Fix bugs or add features via pull requests
5. **Share Knowledge** - Write tutorials or blog posts
6. **Answer Questions** - Help others in discussions

## 🚀 Getting Started

### 1. Fork the Repository

Click the "Fork" button on GitHub to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/microservices-demo.git
cd microservices-demo
```

### 3. Set Up Development Environment

```bash
# Start all services
docker-compose up

# Access the application
open http://localhost
```

See [Quick Start Guide](docs/getting-started/QUICK_START.md) for detailed setup.

### 4. Create a Branch

```bash
# For new features
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b fix/your-bug-fix

# For documentation
git checkout -b docs/your-doc-update
```

### 5. Make Your Changes

- Write clean, documented code
- Follow existing code style
- Add tests for new features
- Update documentation

### 6. Test Your Changes

```bash
# Run tests for affected services
cd user-service && pytest
cd product-service && pytest
cd order-service && pytest

# Test the full application
docker-compose down
docker-compose up --build

# Verify all services are healthy
curl http://localhost/health
```

### 7. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
git add .
git commit -m "feat: add amazing feature"
# or
git commit -m "fix: resolve authentication issue"
# or
git commit -m "docs: update Redis configuration guide"
```

### 8. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 9. Open a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template
5. Submit for review

## 📝 Contribution Guidelines

### Code Style

#### Python (Backend Services)
- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) formatter
- Maximum line length: 100 characters
- Use type hints where appropriate
- Write docstrings for functions and classes

**Example:**
```python
def validate_user(user_id: int) -> bool:
    """
    Validate if a user exists and is active.
    
    Args:
        user_id: The ID of the user to validate
        
    Returns:
        True if user is valid and active, False otherwise
    """
    try:
        user = User.objects.get(id=user_id)
        return user.is_active
    except User.DoesNotExist:
        return False
```

#### JavaScript/React (Frontend)
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use [Prettier](https://prettier.io/) formatter
- Use functional components with hooks
- Use meaningful component and variable names
- Add JSDoc comments for complex functions

**Example:**
```javascript
/**
 * Validates user authentication status
 * @param {Object} user - User object
 * @returns {boolean} True if authenticated
 */
const isAuthenticated = (user) => {
  return user && user.token && !isTokenExpired(user.token)
}
```

#### General Guidelines
- **Comments**: Explain "why", not "what"
- **Naming**: Use descriptive names (no single letters except loops)
- **Functions**: Keep functions small and focused (single responsibility)
- **DRY**: Don't Repeat Yourself - extract common logic
- **KISS**: Keep It Simple, Stupid - avoid over-engineering

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no feature change)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build)
- `perf`: Performance improvements
- `ci`: CI/CD changes

#### Examples

```bash
# Simple commit
feat: add product review feature

# With scope
fix(auth): resolve JWT token expiration issue

# With body
feat(orders): add order cancellation

Allow users to cancel orders within 24 hours of creation.
Adds new API endpoint and updates frontend UI.

# With breaking change
feat(api)!: change authentication endpoint

BREAKING CHANGE: /api/auth/login moved to /api/users/login
```

### Pull Request Guidelines

#### Before Submitting

Ensure your PR meets these requirements:

- ✅ Code follows project style guidelines
- ✅ All tests pass locally
- ✅ New tests added for new features
- ✅ Documentation updated (if needed)
- ✅ No merge conflicts with main branch
- ✅ Commits follow conventional format
- ✅ PR has descriptive title and description

#### PR Title Format

Use the same format as commit messages:

```
feat: add product review feature
fix: resolve authentication timeout
docs: update Redis configuration guide
```

#### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Changes Made
- List specific changes
- Be detailed but concise
- Use bullet points

## Testing
Describe how to test your changes:
1. Step-by-step instructions
2. Expected results
3. Edge cases tested

## Screenshots (if applicable)
Add screenshots for UI changes.

## Related Issues
Closes #123
Relates to #456

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published
```

### Testing Requirements

#### For New Features

**Required:**
- Unit tests for business logic
- Integration tests for API endpoints
- Test coverage should not decrease

**Recommended:**
- Property-based tests for complex logic
- Edge case testing
- Error handling tests

**Example:**
```python
# Unit test
def test_create_order_success():
    """Test successful order creation"""
    order = create_order(user_id=1, items=[{"product_id": 1, "quantity": 2}])
    assert order.status == "pending"
    assert len(order.items) == 1

# Property-based test
@given(st.integers(min_value=1), st.integers(min_value=1, max_value=100))
def test_order_total_calculation(product_price, quantity):
    """Test order total is always price * quantity"""
    order = create_order_with_price(product_price, quantity)
    assert order.total == product_price * quantity
```

#### For Bug Fixes

1. **Add test that reproduces the bug**
2. **Verify test fails before fix**
3. **Apply fix**
4. **Verify test passes after fix**

**Example:**
```python
def test_jwt_token_expiration_bug():
    """
    Test that expired tokens are properly rejected.
    
    Bug: Expired tokens were being accepted due to incorrect
    time comparison in token validation.
    """
    expired_token = create_expired_token()
    with pytest.raises(TokenExpiredError):
        validate_token(expired_token)
```

#### Running Tests

```bash
# Run all tests for a service
cd user-service
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Documentation Requirements

#### When to Update Documentation

Update documentation when you:
- Add new features
- Change API endpoints
- Modify configuration
- Add dependencies
- Change architecture
- Fix bugs that affect usage

#### Documentation Locations

- **README.md** - Main project overview and quick start
- **docs/** - Detailed documentation by topic
- **Code comments** - Complex logic explanation
- **Docstrings** - Function and class documentation
- **API docs** - Swagger/OpenAPI annotations

#### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Explain "why", not just "how"
- Keep it up-to-date

**Example:**
```markdown
## Adding Two-Factor Authentication

Two-factor authentication (2FA) adds an extra layer of security by requiring
users to provide a second form of verification.

### Setup Process

1. User enables 2FA in settings
2. System generates a secret key
3. User scans QR code with authenticator app
4. User enters verification code to confirm setup

### Code Example

\`\`\`python
from django_otp.plugins.otp_totp.models import TOTPDevice

# Create TOTP device for user
device = TOTPDevice.objects.create(
    user=user,
    name='default',
    confirmed=False
)

# Generate QR code URL
qr_url = device.config_url
\`\`\`

### Security Considerations

- Secret keys are never displayed after initial setup
- Backup tokens are hashed before storage
- Time drift tolerance is ±30 seconds
```

## 🔍 Code Review Process

### 1. Automated Checks

When you submit a PR, automated checks run:
- ✅ Tests must pass
- ✅ Code style checks
- ✅ Build verification
- ✅ No merge conflicts

### 2. Manual Review

Maintainers review for:
- Code quality and readability
- Architecture fit
- Security considerations
- Performance implications
- Documentation completeness
- Test coverage

### 3. Feedback and Iteration

- Address review comments
- Update PR as needed
- Discuss design decisions
- Request clarification if needed

### 4. Approval and Merge

- Approved PRs are merged to main
- Commits may be squashed for clean history
- Contributors are credited in release notes

## 🎓 Learning Resources

### Microservices
- [Microservices Patterns](https://microservices.io/patterns/index.html)
- [Building Microservices](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/)

### Django & DRF
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

### React
- [React Documentation](https://react.dev/)
- [React Router](https://reactrouter.com/)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)

## 🤝 Community Guidelines

### Be Respectful
- Treat everyone with respect and kindness
- Welcome newcomers and help them learn
- Be patient with questions
- Provide constructive feedback

### Be Collaborative
- Share knowledge and experience
- Help others solve problems
- Discuss ideas openly
- Credit contributors

### Be Professional
- Keep discussions on-topic
- Avoid personal attacks
- Focus on the code, not the person
- Follow the code of conduct

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be inclusive**: Welcome people of all backgrounds
- **Be respectful**: Disagree respectfully
- **Be collaborative**: Work together
- **Be professional**: Maintain professionalism

**Unacceptable behavior:**
- Harassment or discrimination
- Personal attacks
- Trolling or insulting comments
- Publishing private information
- Other unprofessional conduct

**Reporting:**
If you experience or witness unacceptable behavior, please report it to the project maintainers.

## 🆘 Getting Help

### Questions About Contributing?

- **GitHub Discussions** - Ask questions and share ideas
- **Issues** - Check existing issues for similar questions
- **Documentation** - Read the docs thoroughly
- **Pull Requests** - Ask in PR comments

### Found a Security Issue?

**Do NOT open a public issue!**

- Email security concerns privately
- See [SECURITY.md](SECURITY.md) for details
- We'll respond within 48 hours

## 🎉 Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Project documentation
- Special thanks section

### Hall of Fame

We maintain a list of top contributors who have made significant contributions to the project.

## 📋 Checklist for First-Time Contributors

- [ ] Read this contributing guide
- [ ] Set up development environment
- [ ] Run the application locally
- [ ] Explore the codebase
- [ ] Check existing issues for "good first issue" label
- [ ] Fork the repository
- [ ] Create a branch
- [ ] Make your changes
- [ ] Write tests
- [ ] Update documentation
- [ ] Submit pull request
- [ ] Respond to review feedback

## 🚀 Quick Reference

```bash
# Setup
git clone https://github.com/YOUR_USERNAME/microservices-demo.git
cd microservices-demo
docker-compose up

# Create branch
git checkout -b feature/my-feature

# Make changes and test
# ... edit files ...
pytest
docker-compose up --build

# Commit
git add .
git commit -m "feat: add my feature"

# Push
git push origin feature/my-feature

# Open PR on GitHub
```

---

**Thank you for contributing! Your efforts help make this project better for everyone.** 🎉

For questions, open a discussion or issue on GitHub.
