# 🔄 Continuous Integration (CI/CD) Setup

## GitHub Actions Workflow

FlowSentinel includes automated testing via GitHub Actions.

### Workflow: `.github/workflows/test.yml`

**Triggers:**
- Push to `main` or `master` branch
- Pull requests to `main` or `master` branch

**Jobs:**
1. ✅ **Checkout code** - Get latest code from repository
2. ✅ **Setup Python 3.11** - Install Python with pip caching
3. ✅ **Install dependencies** - Install all required packages
4. ✅ **Lint with flake8** - Check code style and syntax
5. ✅ **Format check with black** - Verify code formatting
6. ✅ **API tests** - Start server and run test suite
7. ✅ **Health check** - Verify server starts successfully

**Estimated runtime:** ~1-2 minutes

---

## Setting Up CI/CD

### 1. Update README Badge

Replace `YOUR_USERNAME` in the badge URL:

```markdown
[![Tests](https://github.com/YOUR_USERNAME/flowsentinel/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/flowsentinel/actions)
```

Change to:
```markdown
[![Tests](https://github.com/nabilhassan/flowsentinel/workflows/Tests/badge.svg)](https://github.com/nabilhassan/flowsentinel/actions)
```

### 2. Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit with CI/CD setup"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/flowsentinel.git

# Push to GitHub
git push -u origin main
```

### 3. Enable GitHub Actions

GitHub Actions should automatically run on push. Check:
- Go to your repository on GitHub
- Click "Actions" tab
- See workflow runs

---

## Local Development with Linting

### Install Dev Dependencies

```bash
# Install development tools
pip install -r requirements-dev.txt

# Or install specific tools
pip install flake8 black isort pylint
```

### Run Linting Locally

```bash
# Lint with flake8
flake8 main.py demo.py test_api.py

# Format with black
black main.py demo.py test_api.py

# Check formatting without changes
black --check main.py demo.py test_api.py

# Sort imports
isort main.py demo.py test_api.py

# Comprehensive linting
pylint main.py
```

### Pre-commit Hooks (Optional)

Install pre-commit to run checks before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml (see below)
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

**`.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
```

---

## CI/CD Best Practices

### 1. Keep Tests Fast
- Current workflow: ~1-2 minutes ✅
- Use caching for pip dependencies
- Run only necessary tests in CI

### 2. Fail Fast
- Syntax errors caught by flake8
- Import errors caught immediately
- Server health check validates startup

### 3. Matrix Testing (Optional)

Test multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11']
```

### 4. Code Coverage (Optional)

Add coverage reporting:

```yaml
- name: Test with coverage
  run: |
    pip install pytest pytest-cov
    pytest --cov=main --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

---

## Troubleshooting CI/CD

### Workflow Fails

**Check logs:**
1. Go to GitHub Actions tab
2. Click on failed workflow
3. Expand failing step
4. Review error messages

**Common issues:**
- Missing dependencies → Update `requirements.txt`
- Linting errors → Run `black` and `flake8` locally first
- Server won't start → Check port conflicts, environment variables

### Local vs CI Differences

```bash
# Test locally first
python main.py &
sleep 5
curl http://localhost:8000/health
python test_api.py
```

### Skip CI for Documentation Changes

```bash
git commit -m "Update README [skip ci]"
```

---

## Status Badges

Add more badges to your README:

```markdown
# Code coverage
[![codecov](https://codecov.io/gh/YOUR_USERNAME/flowsentinel/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/flowsentinel)

# Code quality
[![CodeFactor](https://www.codefactor.io/repository/github/YOUR_USERNAME/flowsentinel/badge)](https://www.codefactor.io/repository/github/YOUR_USERNAME/flowsentinel)

# Dependencies
[![Updates](https://pyup.io/repos/github/YOUR_USERNAME/flowsentinel/shield.svg)](https://pyup.io/repos/github/YOUR_USERNAME/flowsentinel/)
```

---

## Deployment with CI/CD

### Deploy on Successful Tests

Add deployment step to workflow:

```yaml
deploy:
  needs: test
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  
  steps:
    - name: Deploy to production
      run: |
        # Your deployment commands
        echo "Deploying..."
```

---

**Questions? Check GitHub Actions documentation or open an issue!**
