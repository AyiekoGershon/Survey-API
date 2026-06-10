#!/bin/bash
# Setup script for Sky Survey API

echo "Sky Survey API - Setup Script"
echo "=============================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

echo "✓ pip found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your MySQL credentials"
echo "2. Run: mysql -u root -p < database_schema.sql"
echo "3. Run: uvicorn app.main:app --reload"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Swagger UI: http://localhost:8000/docs"
