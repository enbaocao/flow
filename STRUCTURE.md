# Project Structure

```
flow/
├── backend/                    # Python backend
│   ├── __init__.py
│   ├── flow.py                # CLI entry point
│   ├── highlight.py           # Highlight mode script
│   ├── api_server.py          # FastAPI server
│   ├── config.py              # Configuration
│   ├── scorer.py              # Core scoring logic
│   ├── candidate_generator.py # Candidate generation
│   ├── refinement_pipeline.py # Main pipeline
│   ├── semantic_checker.py    # Semantic validation
│   ├── linguistic_constraints.py # POS/morphology checks
│   ├── tokenizer_utils.py     # Tokenization utilities
│   ├── requirements.txt       # Python dependencies
│   ├── requirements-api.txt   # API-specific deps
│   ├── setup.py              # Package setup
│   ├── test_basic.py         # Unit tests
│   └── test_highlight.py     # Highlight tests
│
├── frontend/                  # Next.js frontend
│   ├── app/                  # Next.js app directory
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   └── ...
│
├── scripts/                   # Utility scripts
│   ├── activate.sh           # Activate virtual environment
│   ├── start.sh              # Start both servers
│   └── check_api.sh          # Health check API
│
├── flow                       # CLI wrapper script
├── .gitignore
├── LICENSE
└── README.md
```

## Usage

### CLI
```bash
./flow "Your text here" --highlight
```

### Web Interface
```bash
./scripts/start.sh
```

### Development
```bash
# Backend tests
cd backend
python -m pytest test_basic.py

# Run API server
python -m backend.api_server

# Frontend development
cd frontend
npm run dev
```
