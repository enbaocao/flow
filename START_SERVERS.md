# How to Start the Flow Frontend

This guide shows you how to run the Flow text highlighting system with the web frontend.

## Prerequisites

1. Python virtual environment with Flow dependencies installed
2. Node.js and npm installed
3. FastAPI and uvicorn installed

## Installation Steps

### 1. Install API Server Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate

# Install API server dependencies (using uv)
uv pip install fastapi uvicorn[standard] pydantic

# Or install from requirements file
uv pip install -r requirements-api.txt
```

### 2. Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install
```

## Running the Servers

You need to run TWO servers:

### Terminal 1: Start the Python API Server

```bash
# From the main flow directory
source venv/bin/activate
python api_server.py
```

The API server will start on: **http://localhost:8000**

You should see:
```
Initializing Flow pipeline...
Loading models (this may take a moment)...
All models loaded successfully!
✓ Pipeline initialized and ready!
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal 2: Start the Next.js Frontend

```bash
# From the frontend directory
cd frontend
npm run dev
```

The frontend will start on: **http://localhost:3000**

You should see:
```
▲ Next.js 15.x.x
- Local:        http://localhost:3000
```

## Access the Application

Open your browser and go to:

👉 **http://localhost:3000**

## Using the Application

1. **Paste your text** in the left input area
2. **Click "Analyze Text"** or press Cmd/Ctrl + Enter
3. **View results** on the right side - highlighted words show potential issues
4. **Hover over yellow-highlighted words** to see:
   - Why the word was flagged
   - Replacement suggestions
   - Quality metrics (ΔLL, similarity, etc.)
5. **Adjust settings** using the "Analysis Settings" panel at the top

## Stopping the Servers

- Press `Ctrl+C` in each terminal to stop the respective server

## Troubleshooting

### API Server Won't Start

**Problem:** "Pipeline not initialized" or model loading errors

**Solution:**
```bash
# Make sure spaCy model is installed
python -m spacy download en_core_web_sm

# Verify all dependencies are installed
uv pip install -r requirements.txt
```

### Frontend Won't Connect to API

**Problem:** "Failed to fetch" or CORS errors

**Solution:**
- Make sure the API server is running on port 8000
- Check that `http://localhost:8000/api/health` returns a response
- Verify CORS is properly configured in `api_server.py`

### Port Already in Use

**Problem:** "Address already in use" error

**Solution for API (port 8000):**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Solution for Frontend (port 3000):**
```bash
# Find and kill process using port 3000
lsof -ti:3000 | xargs kill -9
```

Or change the port:
```bash
# Frontend on different port
PORT=3001 npm run dev
```

### Slow Analysis

**Problem:** Text analysis takes a long time

**This is normal!** The first request loads the models into memory and may take 10-30 seconds. Subsequent requests should be faster (2-5 seconds per sentence).

**To speed up:**
- The API server uses `roberta-base` (faster) by default
- Consider using a GPU by changing `device="cpu"` to `device="cuda"` in `api_server.py`

## Quick Start Script

Save this as `start.sh`:

```bash
#!/bin/bash

# Start API server in background
source venv/bin/activate
python api_server.py &
API_PID=$!

# Wait for API to be ready
echo "Waiting for API server to start..."
sleep 5

# Start frontend
cd frontend
npm run dev

# Cleanup on exit
trap "kill $API_PID" EXIT
```

Make it executable and run:
```bash
chmod +x start.sh
./start.sh
```

## Production Deployment

For production deployment, consider:

1. **API Server:**
   - Use a production WSGI server like gunicorn
   - Add authentication/rate limiting
   - Configure proper CORS origins
   - Use environment variables for configuration

2. **Frontend:**
   - Build for production: `npm run build`
   - Use `npm start` or deploy to Vercel/Netlify
   - Update API endpoint URL in environment variables

## Environment Variables

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Server

You can modify these in `api_server.py`:
- `roberta_model`: "roberta-base" or "roberta-large"
- `device`: "cpu" or "cuda"
- `min_entropy`, `min_pll_gain`, etc.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│  Next.js        │  HTTP   │  FastAPI         │
│  Frontend       │ ──────→ │  API Server      │
│  (Port 3000)    │         │  (Port 8000)     │
│                 │         │                  │
└─────────────────┘         └──────────────────┘
                                      │
                                      ↓
                            ┌──────────────────┐
                            │                  │
                            │  Flow Pipeline   │
                            │  (RoBERTa,       │
                            │   SBERT, etc.)   │
                            │                  │
                            └──────────────────┘
```

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - Detailed health status
- `POST /api/highlight` - Analyze text and get highlights
- `GET /docs` - API documentation (Swagger UI)

## Next Steps

- Customize the UI styling in the components
- Add more configuration options
- Implement result export/sharing
- Add user authentication for saved results
- Deploy to production

Enjoy using Flow Highlight! 🚀

