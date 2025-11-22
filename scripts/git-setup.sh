#!/bin/bash

# ============================================================================
# FlowSentinel Git Setup Script
# ============================================================================
# This script initializes Git repository and makes first commit
# ============================================================================

echo ""
echo "🔧 FlowSentinel - Git Setup"
echo "============================"
echo ""

# Check if already a git repo
if [ -d ".git" ]; then
    echo "✅ Git repository already initialized"
    echo ""
    git status
    exit 0
fi

# Initialize git
echo "📦 Initializing Git repository..."
git init

# Add all files
echo "➕ Adding files to Git..."
git add .

# Create first commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: FlowSentinel backend with CI/CD"

echo ""
echo "✅ Git repository initialized!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Create a repository on GitHub: https://github.com/new"
echo ""
echo "2. Add remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/flowsentinel.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Update README.md badge with your username"
echo ""
echo "🎉 Done! Your repository is ready."
echo ""
