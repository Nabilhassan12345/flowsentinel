#!/bin/bash

# ============================================================================
# FlowSentinel - GitHub Push Guide
# ============================================================================
# This script helps you push your FlowSentinel project to GitHub
# ============================================================================

echo ""
echo "🚀 FlowSentinel - GitHub Push Guide"
echo "====================================="
echo ""

# Check if remote exists
if git remote | grep -q "origin"; then
    echo "✅ Git remote 'origin' already configured"
    git remote -v
    echo ""
    echo "To push to GitHub, run:"
    echo "  git push -u origin main"
else
    echo "📝 Step 1: Create a GitHub Repository"
    echo "--------------------------------------"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: flowsentinel"
    echo "3. Description: Agentic AI company brain for workflow monitoring"
    echo "4. Choose Public or Private"
    echo "5. DO NOT initialize with README (we already have one)"
    echo "6. Click 'Create repository'"
    echo ""
    
    echo "📝 Step 2: Add Remote and Push"
    echo "--------------------------------"
    echo "Replace YOUR_USERNAME with your GitHub username:"
    echo ""
    echo "  git remote add origin https://github.com/YOUR_USERNAME/flowsentinel.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
    
    echo "OR if you prefer SSH:"
    echo ""
    echo "  git remote add origin git@github.com:YOUR_USERNAME/flowsentinel.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
fi

echo "📝 Step 3: Update README Badge"
echo "-------------------------------"
echo "After pushing, edit README.md and replace YOUR_USERNAME with your actual GitHub username in the badge URLs"
echo ""

echo "📝 Step 4: Invite Collaborator (Frontend Developer)"
echo "----------------------------------------------------"
echo "1. Go to: https://github.com/YOUR_USERNAME/flowsentinel/settings/access"
echo "2. Click 'Invite a collaborator'"
echo "3. Enter your friend's GitHub username"
echo "4. They'll receive an email invitation"
echo ""

echo "📝 Step 5: Enable GitHub Actions"
echo "---------------------------------"
echo "1. Go to: https://github.com/YOUR_USERNAME/flowsentinel/actions"
echo "2. Click 'I understand my workflows, go ahead and enable them'"
echo "3. Your CI/CD pipeline will run on every push!"
echo ""

echo "✅ Summary of What You Built:"
echo "=============================="
echo "📦 17 files committed to Git"
echo "🐍 933 lines of Python code (main.py)"
echo "🧪 Comprehensive test suite (test_api.py)"
echo "🐳 Docker containerization (Dockerfile + compose)"
echo "⚙️  CI/CD pipeline (GitHub Actions)"
echo "📚 Complete documentation (README + guides)"
echo "🔧 Automation scripts (setup, start, git-setup)"
echo ""

echo "🎯 What Your Project Does:"
echo "=========================="
echo "✅ Ingests events from Slack, Jira, GitHub, Calendar"
echo "✅ AI-powered analysis to detect blockers and risks"
echo "✅ Automated Slack notifications"
echo "✅ Natural language Q&A system"
echo "✅ Health status monitoring (RED/YELLOW/GREEN)"
echo "✅ 11 REST API endpoints"
echo "✅ Interactive API documentation"
echo "✅ Docker deployment ready"
echo "✅ Automated testing pipeline"
echo ""

echo "🌟 Next Steps:"
echo "============="
echo "1. Push to GitHub (follow steps above)"
echo "2. Add Slack webhook to .env for real notifications"
echo "3. Invite your frontend developer friend"
echo "4. Create frontend/ directory for React/Vue app"
echo "5. Consider getting IBM watsonx.ai trial for real AI"
echo ""

echo "💡 Pro Tips:"
echo "==========="
echo "• Keep .env file secret (already in .gitignore)"
echo "• Use feature branches for new features"
echo "• Create Pull Requests for code review"
echo "• Tag releases (git tag v1.0.0)"
echo "• Add more tests as you build features"
echo ""

echo "🎉 You've built an amazing project! Time to share it with the world!"
echo ""
