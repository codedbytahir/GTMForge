#!/bin/bash
# Install missing dependencies

echo "Installing required packages..."

# Activate virtual environment
source venv/bin/activate

# Try installing with SSL workaround
echo "Installing aiohttp..."
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org aiohttp

echo "Installing pillow..."
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pillow

echo "Done! Dependencies installed."

