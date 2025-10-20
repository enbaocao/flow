#!/bin/bash
# Activation script for Flow virtual environment

echo "Activating Flow virtual environment..."
source venv/bin/activate

echo "✓ Virtual environment activated!"
echo "Flow is ready to use:"
echo '  python flow.py "Your text to refine here"'
echo "  python example.py"
echo ""
echo "To deactivate: deactivate"
