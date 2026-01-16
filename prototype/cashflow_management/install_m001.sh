#!/bin/bash
# M001 Installation Script
# Copyright (c) 2026, FaceNet

set -e  # Exit on error

echo ""
echo "=============================================="
echo "🚀 M001: Core Setup - Installation"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get site name from user or use default
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: ./install_m001.sh [site-name]${NC}"
    echo -e "${YELLOW}Using current site...${NC}"
    SITE=$(bench --site currentsite.txt 2>/dev/null || echo "")
    if [ -z "$SITE" ]; then
        echo -e "${RED}❌ No site specified. Please provide site name.${NC}"
        exit 1
    fi
else
    SITE=$1
fi

echo -e "${BLUE}📋 Site: ${SITE}${NC}"
echo ""

# Step 1: Check ERPNext
echo -e "${BLUE}Step 1: Checking ERPNext installation...${NC}"
if bench --site $SITE list-apps | grep -q "erpnext"; then
    echo -e "${GREEN}   ✓ ERPNext is installed${NC}"
else
    echo -e "${YELLOW}   ⚠ ERPNext not found. Installing ERPNext v15...${NC}"
    bench get-app erpnext --branch version-15
    bench --site $SITE install-app erpnext
    echo -e "${GREEN}   ✓ ERPNext installed${NC}"
fi
echo ""

# Step 2: Migrate prototype app
echo -e "${BLUE}Step 2: Migrating prototype app...${NC}"
bench --site $SITE migrate
echo -e "${GREEN}   ✓ Migration completed${NC}"
echo ""

# Step 3: Clear cache
echo -e "${BLUE}Step 3: Clearing cache...${NC}"
bench --site $SITE clear-cache
echo -e "${GREEN}   ✓ Cache cleared${NC}"
echo ""

# Step 4: Build assets
echo -e "${BLUE}Step 4: Building assets...${NC}"
bench build --app prototype
echo -e "${GREEN}   ✓ Assets built${NC}"
echo ""

# Step 5: Setup sample data
echo -e "${BLUE}Step 5: Setting up sample data (optional)...${NC}"
read -p "Do you want to create sample departments and teams? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    bench --site $SITE console <<EOF
from prototype.cashflow_management.setup_m001 import setup_m001
setup_m001()
EOF
    echo -e "${GREEN}   ✓ Sample data created${NC}"
else
    echo -e "${YELLOW}   • Skipped sample data${NC}"
fi
echo ""

# Step 6: Run tests
echo -e "${BLUE}Step 6: Running tests (optional)...${NC}"
read -p "Do you want to run unit tests? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    bench --site $SITE run-tests --doctype "Team" || echo -e "${YELLOW}   ⚠ Some tests may have failed${NC}"
    echo -e "${GREEN}   ✓ Tests completed${NC}"
else
    echo -e "${YELLOW}   • Skipped tests${NC}"
fi
echo ""

# Summary
echo ""
echo "=============================================="
echo -e "${GREEN}✅ M001 Installation Completed!${NC}"
echo "=============================================="
echo ""
echo "📚 Next Steps:"
echo "   1. Visit: http://localhost:8000/app/team"
echo "   2. Create your first team"
echo "   3. Assign employees to teams"
echo "   4. Read: apps/prototype/prototype/cashflow_management/M001-README.md"
echo ""
echo "🧪 Testing:"
echo "   bench --site $SITE run-tests --doctype 'Team'"
echo ""
echo "📊 Create sample data manually:"
echo "   bench --site $SITE console"
echo "   >>> from prototype.cashflow_management.setup_m001 import setup_m001"
echo "   >>> setup_m001()"
echo ""
