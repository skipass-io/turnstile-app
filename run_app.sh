#!/bin/bash

# Get the directory where the script is located
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

# Print the base directory
echo "Run turnstile-app from: $BASE_DIR"

# Activate the virtual environment
source "$BASE_DIR/env/bin/activate"

# Run the Python script
python "$BASE_DIR/app/main.py" "$@"

# Deactivate the virtual environment
deactivate
