#!/bin/bash

# Simple push script - just add your GitHub username

echo "🚀 FlowSentinel - Quick Push to GitHub"
echo "======================================"
echo ""

# Ask for GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Error: GitHub username is required"
    exit 1
fi

echo ""
echo "📦 Setting up remote for: https://github.com/$GITHUB_USERNAME/flowsentinel.git"
echo ""

# Add remote
git remote add origin "https://github.com/$GITHUB_USERNAME/flowsentinel.git" 2>/dev/null

# If remote already exists, update it
if [ $? -ne 0 ]; then
    echo "ℹ️  Remote already exists, updating..."
    git remote set-url origin "https://github.com/$GITHUB_USERNAME/flowsentinel.git"
fi

# Show what we're about to push
echo ""
echo "📊 Ready to push:"
git log --oneline -3
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Your code is now on GitHub!"
    echo ""
    echo "🌐 View your repository at:"
    echo "   https://github.com/$GITHUB_USERNAME/flowsentinel"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Update README.md badge with your username"
    echo "   2. Enable GitHub Actions"
    echo "   3. Invite collaborators"
    echo ""
else
    echo ""
    echo "❌ Push failed. This might be because:"
    echo "   1. Repository doesn't exist yet - create it at https://github.com/new"
    echo "   2. You need to authenticate - GitHub will prompt you"
    echo "   3. You don't have permission - check repository access"
    echo ""
fi
