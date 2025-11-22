# 📚 FlowSentinel Documentation

Quick links to all documentation and guides.

---

## 🚀 Getting Started

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete beginner guide (start here!)
- **[README.md](README.md)** - Full project documentation
- **[STRUCTURE.md](STRUCTURE.md)** - Project organization explained

---

## 📖 Guides & Tutorials

- **[docs/DOCKER.md](docs/DOCKER.md)** - Docker deployment guide
- **[docs/CI-CD.md](docs/CI-CD.md)** - Continuous integration setup

---

## 🛠️ Scripts & Tools

All scripts are in the `scripts/` folder:

- **`setup.sh`** - Complete project setup (venv + dependencies)
- **`start.sh`** - Start FlowSentinel server
- **`git-setup.sh`** - Initialize Git repository
- **`quick-push.sh`** - Interactive GitHub push
- **`PUSH_TO_GITHUB.sh`** - Detailed push instructions

**Usage:**
```bash
./scripts/setup.sh   # Run once
./scripts/start.sh   # Run every time
```

---

## 🧪 Testing & Demo

Located in `tests/` folder:

- **`test_api.py`** - Comprehensive test suite
- **`demo.py`** - Interactive demonstration

**Usage:**
```bash
python tests/test_api.py  # Run all tests
python tests/demo.py      # See demo
```

---

## 📁 Project Structure

```
flowsentinel/
├── src/            # Source code (main.py)
├── tests/          # Tests and demos
├── scripts/        # Automation scripts  
├── docs/           # Documentation
├── .github/        # GitHub Actions
└── README.md       # Main documentation
```

See [STRUCTURE.md](STRUCTURE.md) for detailed breakdown.

---

## ⚡ Quick Commands

```bash
# Setup (first time)
./scripts/setup.sh

# Start server
./scripts/start.sh

# Run tests
python tests/test_api.py

# View API docs
open http://localhost:8000/docs
```

---

## 🎯 What to Read First

1. **New to FlowSentinel?** → [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Want full details?** → [README.md](README.md)
3. **Need Docker?** → [docs/DOCKER.md](docs/DOCKER.md)
4. **Setting up CI/CD?** → [docs/CI-CD.md](docs/CI-CD.md)
5. **Understanding structure?** → [STRUCTURE.md](STRUCTURE.md)

---

**Start here: [GETTING_STARTED.md](GETTING_STARTED.md)** 🚀
