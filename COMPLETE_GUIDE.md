# Flow with Web Frontend - Complete Guide

## 🎉 What Was Built

You now have **TWO interfaces** for Flow's text highlighting:

### 1. Command-Line Interface (Original)
```bash
python flow.py "Your text" --highlight
```

### 2. Web Interface (NEW!) 🆕
Beautiful Next.js + Tailwind CSS frontend with:
- Modern, responsive UI
- Interactive tooltips
- Real-time analysis
- Configurable settings

## 🚀 Quick Start

### Option 1: Use the Startup Script (Easiest!)

```bash
# Make sure you're in the flow directory
cd /Users/enbao/projects/flow

# Run the startup script
./start.sh
```

This will:
1. Start the API server (Python backend)
2. Start the Next.js frontend
3. Open your browser to http://localhost:3000

### Option 2: Manual Startup

**Terminal 1 - Start API Server:**
```bash
cd /Users/enbao/projects/flow
source venv/bin/activate
pip install fastapi uvicorn pydantic  # First time only
python api_server.py
```

**Terminal 2 - Start Frontend:**
```bash
cd /Users/enbao/projects/flow/frontend
npm install  # First time only
npm run dev
```

**Open Browser:**
Navigate to http://localhost:3000

## 📦 First-Time Setup

### Install API Dependencies

```bash
source venv/bin/activate
uv pip install -r requirements-api.txt
```

Or manually:
```bash
uv pip install fastapi uvicorn pydantic
```

### Install Frontend Dependencies

```bash
cd frontend
npm install
```

## 🎨 Using the Web Interface

### Step-by-Step

1. **Open http://localhost:3000** in your browser

2. **Paste your text** in the left input area
   - Example: "The utilize of technology has revolutionized our lives."

3. **Click "Analyze Text"** (or press Cmd/Ctrl + Enter)
   - Wait 2-5 seconds for analysis

4. **View results** on the right side
   - Yellow highlighting = words that need editing
   - Hover over highlighted words for details

5. **Adjust settings** (optional)
   - Click "Analysis Settings" at the top
   - Try presets: Conservative, Balanced, or Aggressive
   - Or use sliders to fine-tune

### Understanding the Interface

#### Left Panel: Input
- **Text area** - Paste or type your text
- **Character counter** - Shows text length
- **Clear button** - Reset input
- **Analyze button** - Start analysis

#### Right Panel: Results
- **Highlighted text** - Yellow = flagged words
- **Hover tooltips** - Detailed info on each word
- **Success message** - "No issues detected" if text is good

#### Top Panel: Settings
- **Sensitivity presets** - Quick configuration
- **Min Entropy slider** - 3.0 to 6.0 (higher = less sensitive)
- **Max Rank slider** - 10 to 200 (lower = more strict)
- **Suggestions slider** - 1 to 5 per word

### Tooltip Information

When you hover over a highlighted word, you'll see:

```
📝 'utilize'
   Entropy: 5.60 bits | Rank: #8131
   Flagged: high uncertainty, low rank
   
   Top replacements:
   ✓ use            → ΔLL= +5.20 | sim=0.967
     adoption       → ΔLL= +3.40 | sim=0.952
     implementation → ΔLL= +0.80 | sim=0.948
```

**What it means:**
- **✓** = This suggestion passes all quality checks (safe to use!)
- **ΔLL** = Fluency improvement (higher = better)
- **sim** = Semantic similarity (closer to 1 = meaning preserved)

## 🎛️ Configuration Guide

### Sensitivity Levels

**Conservative** (min_entropy=5.0, max_rank=20)
- Only flags very obvious problems
- Fewer false positives
- May miss some issues

**Balanced** (min_entropy=4.0, max_rank=50) ⭐ Recommended
- Good middle ground
- Catches most issues
- Few false positives

**Aggressive** (min_entropy=3.5, max_rank=100)
- Catches more potential issues
- More false positives
- Good for careful editing

### Parameter Details

**Minimum Entropy Threshold**
- What: Measures uncertainty about a word
- Range: 3.0 - 6.0 bits
- Lower = more sensitive (flags more words)
- Higher = less sensitive (only obvious issues)

**Maximum Original Rank**
- What: Position in probability distribution
- Range: 10 - 200
- Lower = more strict (only very unexpected words)
- Higher = less strict (catch borderline cases)

**Suggestions per Word**
- What: How many replacements to show
- Range: 1 - 5
- More suggestions = more options but more cluttered

## 🏗️ Architecture

```
┌─────────────────────┐
│   Web Browser       │
│  (localhost:3000)   │
│                     │
│  Next.js Frontend   │
└──────────┬──────────┘
           │
           │ HTTP POST /api/highlight
           │
┌──────────▼──────────┐
│   API Server        │
│  (localhost:8000)   │
│                     │
│  FastAPI + Flow     │
│  Pipeline           │
└─────────────────────┘
```

## 📊 What Each Interface Is Good For

### Command-Line Interface
**Best for:**
- Quick checks
- Batch processing
- Scripting/automation
- Terminal workflows

**Commands:**
```bash
# Basic highlighting
python flow.py "text" --highlight

# From file
python flow.py --file doc.txt --highlight

# With options
python flow.py "text" --highlight --min-entropy 3.5
```

### Web Interface  
**Best for:**
- Interactive analysis
- Visual feedback
- Exploring suggestions
- Non-technical users
- Sharing with others

**Access:**
Just open http://localhost:3000

## 🔧 Troubleshooting

### API Server Won't Start

**Problem:** "Module not found" error

**Solution:**
```bash
source venv/bin/activate
uv pip install fastapi uvicorn pydantic
```

**Problem:** "Pipeline not initialized"

**Solution:**
```bash
python -m spacy download en_core_web_sm
uv pip install -r requirements.txt
```

### Frontend Won't Connect

**Problem:** "Failed to fetch" or network error

**Solution:**
1. Make sure API server is running on port 8000
2. Check: http://localhost:8000/api/health
3. Look for CORS errors in browser console

### Port Already in Use

**For port 8000 (API):**
```bash
lsof -ti:8000 | xargs kill -9
```

**For port 3000 (Frontend):**
```bash
lsof -ti:3000 | xargs kill -9
```

Or use different port:
```bash
PORT=3001 npm run dev
```

### Slow Analysis

**This is normal!**
- First request: 10-30 seconds (loading models)
- Subsequent requests: 2-5 seconds

**To speed up:**
- Use GPU: Change `device="cpu"` to `device="cuda"` in `api_server.py`
- Use smaller model (already using `roberta-base`)

## 📁 Project Structure

```
flow/
├── api_server.py              # FastAPI backend
├── requirements-api.txt       # API dependencies
├── start.sh                   # Startup script
├── flow.py                    # CLI interface
├── highlight.py               # Simple CLI script
├── refinement_pipeline.py     # Core pipeline
├── START_SERVERS.md           # Setup guide
├── FRONTEND_SUMMARY.md        # Frontend docs
└── frontend/                  # Next.js app
    ├── app/
    │   ├── components/
    │   │   ├── TextInput.tsx
    │   │   ├── HighlightedText.tsx
    │   │   └── Controls.tsx
    │   ├── types.ts
    │   ├── page.tsx
    │   └── layout.tsx
    └── package.json
```

## 🎯 Common Workflows

### Quick Draft Check

**Web Interface:**
1. Open http://localhost:3000
2. Paste paragraph
3. Click "Analyze Text"
4. Review highlighted words

**CLI:**
```bash
python flow.py "Your paragraph" --highlight
```

### Important Document

**Web Interface:**
1. Open http://localhost:3000
2. Set sensitivity to "Conservative"
3. Paste each paragraph
4. Review all suggestions carefully

**CLI:**
```bash
python flow.py --file doc.txt --highlight --min-entropy 5.0
```

### Batch Processing

**CLI (recommended):**
```bash
for file in *.txt; do
    python flow.py --file "$file" --highlight > "${file}.analysis"
done
```

## 🌐 API Endpoints

The API server exposes these endpoints:

- `GET /` - Health check
- `GET /api/health` - Detailed status
- `POST /api/highlight` - Analyze text
- `GET /docs` - Interactive API documentation (Swagger UI)

**View API docs:** http://localhost:8000/docs

## 🚦 Status Indicators

### In the Web Interface

**Green checkmark ✓**
- Suggestion passes all quality checks
- Safe to use

**Green "No issues detected" message**
- Your text is already good!
- No words flagged

**Yellow highlighting**
- Word might need editing
- Hover for suggestions

**Red error message**
- Something went wrong
- Check console or API server logs

## 💡 Tips for Best Results

1. **Start with Balanced settings** - The defaults work well
2. **Trust the ✓ marks** - These pass all quality checks
3. **Context matters** - Consider your audience and style
4. **Use presets first** - Then fine-tune if needed
5. **Check multiple paragraphs** - One at a time for best results

## 📚 Additional Documentation

- **START_SERVERS.md** - Detailed setup guide
- **FRONTEND_SUMMARY.md** - Frontend architecture
- **HIGHLIGHT_GUIDE.md** - CLI highlighting guide
- **QUICKSTART.md** - Quick reference
- **README.md** - Main documentation

## 🎓 Learning the System

### Day 1: Get Started
1. Run `./start.sh`
2. Try the example: "The utilize of technology"
3. Hover over "utilize" to see suggestions
4. Try different sensitivity levels

### Day 2: Explore Settings
1. Try all three presets
2. Adjust sliders to see effects
3. Test with your own writing

### Day 3: Integrate
1. Use it for real work
2. Try both CLI and web interface
3. Find your preferred workflow

## 🎉 You're Ready!

### Start the System

```bash
./start.sh
```

### Open Your Browser

http://localhost:3000

### Start Analyzing!

Paste your text and click "Analyze Text"

---

**Need help?**
- Check START_SERVERS.md for detailed setup
- Open http://localhost:8000/docs for API documentation
- See FRONTEND_SUMMARY.md for architecture details

**Enjoy using Flow! ✨**

