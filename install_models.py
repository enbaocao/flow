#!/usr/bin/env python3
"""
Install and download required models for Flow.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Command: {cmd}")
        print(f"  Error: {e.stderr}")
        return False


def check_python_packages():
    """Check if required Python packages are installed."""
    print("Checking Python packages...")
    
    required_packages = [
        'torch', 'transformers', 'sentence-transformers',
        'spacy', 'numpy', 'scipy', 'tqdm'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing.append(package)
    
    return missing


def main():
    """Main installation script."""
    print("=" * 60)
    print("Flow Text Refinement System - Model Installation")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("Error: requirements.txt not found. Run this script from the Flow project directory.")
        return 1
    
    # Install Python packages if needed
    missing_packages = check_python_packages()
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        if not run_command("pip install -r requirements.txt", "Installing Python packages"):
            return 1
    else:
        print("\n✓ All Python packages already installed")
    
    print("\n" + "─" * 60)
    print("Downloading Models")
    print("─" * 60)
    
    # Download spaCy model
    print("\n1. spaCy English model...")
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy model"):
        print("   Note: You may need to run this manually if the download fails")
    
    # Test model downloads by importing
    print("\n" + "─" * 60)
    print("Testing Model Loading")
    print("─" * 60)
    
    try:
        print("\n2. Testing Transformers models...")
        from transformers import AutoTokenizer, AutoModelForMaskedLM
        print("   Loading RoBERTa tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("roberta-base")
        print("✓ RoBERTa tokenizer loaded")
        
        print("   Loading RoBERTa model (this may take a moment)...")
        model = AutoModelForMaskedLM.from_pretrained("roberta-base")
        print("✓ RoBERTa model loaded")
        
    except Exception as e:
        print(f"✗ Error loading RoBERTa models: {e}")
        print("   The models will be downloaded automatically on first use.")
    
    try:
        print("\n3. Testing Sentence-BERT...")
        from sentence_transformers import SentenceTransformer
        print("   Loading SBERT model...")
        sbert = SentenceTransformer("all-MiniLM-L6-v2")
        print("✓ Sentence-BERT model loaded")
        
    except Exception as e:
        print(f"✗ Error loading SBERT model: {e}")
        print("   The model will be downloaded automatically on first use.")
    
    try:
        print("\n4. Testing spaCy...")
        import spacy
        print("   Loading spaCy model...")
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model loaded")
        
    except Exception as e:
        print(f"✗ Error loading spaCy model: {e}")
        print("   Please run: python -m spacy download en_core_web_sm")
        return 1
    
    print("\n" + "=" * 60)
    print("Installation Complete!")
    print("=" * 60)
    print()
    print("You can now use Flow:")
    print('  python flow.py "Your text to refine here"')
    print("  python example.py  # Run examples")
    print()
    print("For help:")
    print("  python flow.py --help")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
