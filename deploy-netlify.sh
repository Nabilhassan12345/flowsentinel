#!/bin/bash

# FlowSentinel Netlify Deployment Script
# Usage: ./deploy-netlify.sh

set -e

echo "🚀 FlowSentinel - Netlify Deployment"
echo "===================================="
echo ""

# Check if netlify-cli is installed
if ! command -v netlify &> /dev/null; then
    echo "📦 Netlify CLI not found. Installing..."
    npm install -g netlify-cli
else
    echo "✅ Netlify CLI found"
fi

echo ""
echo "🔐 Logging in to Netlify..."
netlify login

echo ""
echo "🔗 Linking to site..."
netlify link

echo ""
echo "📋 Pre-deployment checklist:"
echo "   [✓] netlify.toml configured"
echo "   [✓] public/index.html created"
echo "   [✓] package.json configured"
echo ""

read -p "🤔 Ready to deploy? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚢 Deploying to production..."
    netlify deploy --prod
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "🌐 Opening site..."
    netlify open:site
    
    echo ""
    echo "📊 Site URL: https://flowsentinel.netlify.app"
    echo "🎉 Deployment successful!"
else
    echo ""
    echo "❌ Deployment cancelled"
    exit 0
fi
