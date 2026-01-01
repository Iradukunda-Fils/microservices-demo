# Git Setup Guide

## Current Status

✅ Repository is clean - no submodule configuration exists  
✅ All directories are regular directories (not submodules)  
✅ Ready for initial commit

## Initial Setup

### 1. Initialize Git Repository (if not already done)

```bash
git init
```

### 2. Add All Files

```bash
git add .
```

### 3. Create Initial Commit

```bash
git commit -m "feat: initial commit - microservices demo project

- Add user service with JWT authentication and 2FA
- Add product service with catalog management
- Add order service with cross-service validation
- Add React frontend with Tailwind CSS
- Add API gateway with Nginx
- Add Redis cache configuration
- Add Docker Compose for development and production
- Add comprehensive documentation
- Add LICENSE (MIT)
- Add CONTRIBUTING.md
- Add SECURITY.md"
```

### 4. Add Remote Repository

```bash
# Replace with your repository URL
git remote add origin https://github.com/YOUR_USERNAME/microservices-demo.git
```

### 5. Push to Remote

```bash
# First push
git push -u origin main

# Or if using master branch
git branch -M main
git push -u origin main
```

## Verify No Submodules

To confirm there are no submodules:

```bash
# Check for .gitmodules file (should not exist)
ls -la .gitmodules

# Check Git configuration
git config --list | grep submodule

# Check status
git status
```

## Directory Structure

All directories are now regular directories:

```
.
├── api-gateway/          # Regular directory
├── docs/                 # Regular directory
├── frontend/             # Regular directory
├── order-service/        # Regular directory (NOT a submodule)
├── product-service/      # Regular directory (NOT a submodule)
├── scripts/              # Regular directory
└── user-service/         # Regular directory
```

## Common Git Commands

### Check Status
```bash
git status
```

### Add Files
```bash
# Add all files
git add .

# Add specific file
git add README.md

# Add specific directory
git add docs/
```

### Commit Changes
```bash
# With message
git commit -m "feat: add new feature"

# With detailed message
git commit -m "feat: add product reviews

- Add Review model
- Add review API endpoints
- Update frontend to display reviews"
```

### Push Changes
```bash
# Push to main branch
git push origin main

# Force push (use with caution)
git push -f origin main
```

### Pull Changes
```bash
# Pull from main branch
git pull origin main

# Pull with rebase
git pull --rebase origin main
```

### Branch Management
```bash
# Create new branch
git checkout -b feature/my-feature

# Switch to existing branch
git checkout main

# List branches
git branch -a

# Delete branch
git branch -d feature/my-feature
```

## .gitignore Configuration

The `.gitignore` file is already configured to exclude:

- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments (`.venv`, `venv`)
- Node modules (`node_modules/`)
- Environment files (`.env`, `.env.local`)
- Database files (`*.sqlite3`, `db.sqlite3`)
- IDE files (`.vscode/`, `.idea/`)
- Build artifacts (`dist/`, `build/`)
- Docker volumes data
- Log files (`*.log`)

## Troubleshooting

### If You See Submodule Warnings

If you see warnings about submodules, run:

```bash
# Remove .gitmodules if it exists
rm -f .gitmodules

# Remove submodule cache
git rm --cached order-service -f
git rm --cached product-service -f

# Clean Git configuration
git config --remove-section submodule.order-service
git config --remove-section submodule.product-service

# Commit the changes
git add .
git commit -m "fix: remove submodule configuration"
```

### Reset to Clean State

If you need to start fresh:

```bash
# Remove Git directory (WARNING: loses all history)
rm -rf .git

# Reinitialize
git init
git add .
git commit -m "feat: initial commit"
```

## Best Practices

1. **Commit Often**: Make small, focused commits
2. **Write Good Messages**: Use conventional commit format
3. **Pull Before Push**: Always pull latest changes first
4. **Use Branches**: Create feature branches for new work
5. **Review Changes**: Use `git diff` before committing
6. **Keep .gitignore Updated**: Add patterns for files to ignore

## Conventional Commits

Follow this format for commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```bash
feat: add product review feature
fix: resolve JWT token expiration
docs: update Redis configuration guide
style: format code with Black
refactor: extract validation logic
test: add property-based tests
chore: update dependencies
```

## GitHub Setup

### Create Repository on GitHub

1. Go to https://github.com/new
2. Enter repository name: `microservices-demo`
3. Choose public or private
4. **Do NOT** initialize with README (we already have one)
5. Click "Create repository"

### Connect Local to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/microservices-demo.git

# Verify remote
git remote -v

# Push
git push -u origin main
```

### Set Up Branch Protection (Optional)

On GitHub:
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date

## Next Steps

1. ✅ Verify no submodules: `git status`
2. ✅ Add all files: `git add .`
3. ✅ Create initial commit: `git commit -m "feat: initial commit"`
4. ✅ Add remote: `git remote add origin <URL>`
5. ✅ Push to GitHub: `git push -u origin main`

---

**Your repository is ready to go!** 🚀
