#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

# Pull the latest updates from the main branch
git pull origin main

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install pip-tools if not already installed
pip install pip-tools

# Sync the virtual environment with requirements.txt
pip-sync requirements.txt

# Run the main script
python main.py

# Deactivate the virtual environment
deactivate
