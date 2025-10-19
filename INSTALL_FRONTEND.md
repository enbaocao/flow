# Installing Flow Frontend - Quick Guide

## Prerequisites

✅ You already have:
- Python virtual environment created with `uv`
- Flow dependencies installed
- Node.js and npm installed

## Installation Steps

### 1. Install Python API Dependencies

```bash
# Make sure you're in the flow directory
cd /Users/enbao/projects/flow

# Activate virtual environment
source venv/bin/activate

# Install API server dependencies using uv
uv pip install -r requirements-api.txt
```

Or install individually:
```bash
uv pip install fastapi uvicorn[standard] pydantic
```

### 2. Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js packages
npm install
```

### 3. Start the Servers

```bash
# Go back to main directory
cd ..

# Run the startup script
./start.sh
```

Or start manually (two terminals):

**Terminal 1 - API Server:**
```bash
source venv/bin/activate
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Open Your Browser

Navigate to: **http://localhost:3000**

## Verify Installation

### Check API Server

```bash
# Should return health status
curl http://localhost:8000/api/health
```

### Check Frontend

Open http://localhost:3000 - you should see the Flow Highlight interface

## Common Issues

### "Module not found: fastapi"

```bash
source venv/bin/activate
uv pip install -r requirements-api.txt
```

### "command not found: uv"

Install uv first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Frontend won't start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## What Gets Installed

### Python Packages (via uv)
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

### Node Packages (via npm)
- `next` - React framework
- `react` - UI library
- `tailwindcss` - Styling
- `typescript` - Type safety
- And their dependencies (~50 packages total)

## Using uv Instead of pip

Since you set up your environment with `uv`, always use:

```bash
# Instead of: pip install package
uv pip install package

# Instead of: pip install -r requirements.txt
uv pip install -r requirements.txt

# List installed packages
uv pip list

# Uninstall
uv pip uninstall package
```

## Benefits of uv

- ⚡ **Much faster** than regular pip
- 🔒 **Better dependency resolution**
- 💾 **Efficient caching**
- 🎯 **More reliable**

## Next Steps

Once installed, you're ready to use Flow!

### Try the Example

1. Open http://localhost:3000
2. Paste: "The utilize of advanced technology is important."
3. Click "Analyze Text"
4. Hover over "utilize" to see suggestions

### Read the Guides

- **COMPLETE_GUIDE.md** - Full documentation
- **START_SERVERS.md** - Server management
- **WHATS_NEW.md** - Feature overview

Enjoy Flow! 🚀

