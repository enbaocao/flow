# Flow - Quick Start Guide

## Installation

```bash
# Clone and setup
git clone <repo-url>
cd flow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Test it works
python test_basic.py
```

## Three Simple Commands

### 1. Highlight (Identify Issues) 🆕

```bash
python flow.py "Your text here" --highlight
```

**What it does:** Shows you which words need editing and suggests replacements.

**Example:**
```bash
python flow.py "The utilize of technology is important." --highlight
```

### 2. Interactive (Manual Control)

```bash
python flow.py "Your text here" --interactive
```

**What it does:** Asks you to approve each edit one-by-one.

### 3. Apply (Automatic)

```bash
python flow.py "Your text here" --apply-edits
```

**What it does:** Automatically improves the text.

## Quick Reference

| Want to... | Command |
|-----------|---------|
| **See what needs editing** | `python flow.py "text" --highlight` |
| **Fix automatically** | `python flow.py "text" --apply-edits` |
| **Approve each change** | `python flow.py "text" --interactive` |
| **Process a file** | `python flow.py --file input.txt --highlight` |
| **Save to file** | `python flow.py --file input.txt --output result.txt --apply-edits` |
| **Faster analysis** | Add `--model roberta-base` |
| **More thorough** | Add `--model roberta-large` |
| **More sensitive** | Add `--min-entropy 3.5` |
| **Less sensitive** | Add `--min-entropy 5.0` |

## Understanding the Output

When you see:
```
📝 'utilize'
   Entropy: 5.60 bits | Rank: #8131
   Top replacements:
   ✓ 1. use            → ΔLL= +5.20 | sim=0.967
```

This means:
- 📝 The word "utilize" is flagged
- **Entropy 5.60** - High uncertainty (awkward word choice)
- **Rank #8131** - Very low in model's predictions
- **✓** - This suggestion passes all quality checks
- **ΔLL +5.20** - Makes the sentence more fluent
- **sim 0.967** - Preserves meaning (96.7% similar)

## Common Usage Patterns

### Check an email draft
```bash
python highlight.py "Your email text here..."
```

### Improve a document
```bash
python flow.py --file document.txt --output improved.txt --interactive
```

### Quick paragraph check
```bash
python flow.py "Paste your paragraph here" --highlight
```

### Batch process files
```bash
for file in *.txt; do
    python flow.py --file "$file" --highlight
done
```

## What to Expect

- **Fast mode** (roberta-base): ~2-5 seconds per sentence
- **Accurate mode** (roberta-large): ~5-10 seconds per sentence
- **Typical findings**: 0-2 words flagged per sentence
- **Suggestions**: Top 3-5 replacements shown per word

## Tips for Best Results

1. ✅ Start with `--highlight` to see what's flagged
2. ✅ Look for the ✓ mark on suggestions
3. ✅ Use `roberta-base` for speed, `roberta-large` for accuracy
4. ✅ Trust your judgment - you make the final call
5. ✅ Use `--interactive` for important documents

## Need Help?

- Full documentation: `README.md`
- Detailed examples: `USAGE_EXAMPLES.md`
- Highlight guide: `HIGHLIGHT_GUIDE.md`
- Command help: `python flow.py --help`

## Python API (One-liner)

```python
from config import FlowConfig
from refinement_pipeline import RefinementPipeline

pipeline = RefinementPipeline(FlowConfig(roberta_model="roberta-base"))
pipeline.highlight_clunky_words("Your text here", show_top_replacements=3)
```

## Next Steps

Once you're comfortable with the basics:

1. Try tuning thresholds for your writing style
2. Explore the different modes (highlight, interactive, auto)
3. Set up batch processing for your workflow
4. Integrate into your text editor or IDE

Happy writing! ✨

