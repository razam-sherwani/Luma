#!/bin/bash

# ProviderPulse Development Script
# This script starts both Django server and Tailwind CSS compiler in watch mode

echo "🚀 Starting ProviderPulse Development Environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run Django server
start_django() {
    echo -e "${BLUE}📱 Starting Django development server...${NC}"
    source venv/bin/activate
    python manage.py runserver
}

# Function to run Tailwind CSS
start_tailwind() {
    echo -e "${GREEN}🎨 Starting Tailwind CSS compiler...${NC}"
    npm run dev
}

# Create a trap to kill background processes when the script exits
trap 'kill $(jobs -p) 2>/dev/null' EXIT

echo -e "${YELLOW}🔧 Building initial CSS...${NC}"
npm run build

echo -e "${GREEN}✅ Starting development servers...${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop all servers${NC}"
echo ""

# Start Tailwind CSS in the background
start_tailwind &

# Wait a moment for Tailwind to start
sleep 2

# Start Django server (this will block)
start_django