#!/bin/bash
# ============================================================================
# FlowSentinel PostgreSQL Quick Setup Script
# ============================================================================
# This script automates the PostgreSQL setup using Docker
#
# Usage:
#   chmod +x scripts/setup-postgres.sh
#   ./scripts/setup-postgres.sh
# ============================================================================

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "============================================================================"
echo "  🐘 FlowSentinel PostgreSQL Setup"
echo "============================================================================"
echo ""

# Check if Docker is installed
echo -e "${BLUE}[1/6]${NC} Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo ""
    echo "Please install Docker Desktop:"
    echo "  macOS/Windows: https://www.docker.com/products/docker-desktop"
    echo "  Linux: https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi
echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"

# Check if Docker is running
echo -e "${BLUE}[2/6]${NC} Checking if Docker is running..."
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo ""
    echo "Please start Docker Desktop and try again."
    echo ""
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

# Stop existing container if running
echo -e "${BLUE}[3/6]${NC} Checking for existing PostgreSQL container..."
if docker ps -a --format '{{.Names}}' | grep -q '^flowsentinel-db$'; then
    echo -e "${YELLOW}⚠️  Found existing container, stopping and removing...${NC}"
    docker stop flowsentinel-db &> /dev/null || true
    docker rm flowsentinel-db &> /dev/null || true
    echo -e "${GREEN}✅ Cleaned up existing container${NC}"
else
    echo -e "${GREEN}✅ No existing container found${NC}"
fi

# Start PostgreSQL with Docker Compose
echo -e "${BLUE}[4/6]${NC} Starting PostgreSQL container..."
docker-compose up -d postgres
echo -e "${GREEN}✅ PostgreSQL container started${NC}"

# Wait for PostgreSQL to be ready
echo -e "${BLUE}[5/6]${NC} Waiting for PostgreSQL to be ready..."
sleep 5

# Try to connect for up to 30 seconds
TIMEOUT=30
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if docker exec flowsentinel-db pg_isready -U flowsentinel -d flowsentinel &> /dev/null; then
        echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"
        break
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    echo -e "${RED}❌ PostgreSQL failed to start within ${TIMEOUT} seconds${NC}"
    echo ""
    echo "Check logs with: docker-compose logs postgres"
    exit 1
fi

# Test connection
echo -e "${BLUE}[6/6]${NC} Testing database connection..."
DB_VERSION=$(docker exec flowsentinel-db psql -U flowsentinel -d flowsentinel -t -c "SELECT version();" 2>/dev/null | head -n1)
if [ -n "$DB_VERSION" ]; then
    echo -e "${GREEN}✅ Database connection successful!${NC}"
    echo -e "${BLUE}   Version: ${DB_VERSION}${NC}"
else
    echo -e "${RED}❌ Failed to connect to database${NC}"
    exit 1
fi

# Display connection info
echo ""
echo "============================================================================"
echo -e "  ${GREEN}🎉 PostgreSQL Setup Complete!${NC}"
echo "============================================================================"
echo ""
echo "📋 Connection Details:"
echo "  • Host:     localhost"
echo "  • Port:     5432"
echo "  • Database: flowsentinel"
echo "  • Username: flowsentinel"
echo "  • Password: flowsentinel123"
echo ""
echo "🔗 Connection String:"
echo "  postgresql://flowsentinel:flowsentinel123@localhost:5432/flowsentinel"
echo ""
echo "📝 Next Steps:"
echo "  1. Start backend:    cd src && python main.py"
echo "  2. Open Swagger UI:  http://localhost:8000/docs"
echo "  3. Test endpoints:   POST /simulation/run"
echo ""
echo "🛠️  Useful Commands:"
echo "  • View logs:         docker-compose logs postgres"
echo "  • Stop database:     docker-compose stop postgres"
echo "  • Restart database:  docker-compose restart postgres"
echo "  • Remove database:   docker-compose down -v  (⚠️  deletes data!)"
echo ""
echo "============================================================================"
echo ""
