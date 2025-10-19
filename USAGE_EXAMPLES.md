# Flow - Usage Examples

This document provides practical examples for using Flow's different modes.

## Mode Comparison

| Mode | Purpose | Command |
|------|---------|---------|
| **Highlight** | Identify words that need editing | `--highlight` |
| **Show Candidates** | See all possible replacements | default or `--show-candidates N` |
| **Apply Edits** | Automatically apply improvements | `--apply-edits` |
| **Interactive** | Manually approve each edit | `--interactive` |

## 1. Highlight Mode (Quick Analysis) 🆕

**When to use:** You want to quickly see which words might need editing without detailed analysis.

```bash
# Basic usage
python flow.py "The utilize of technology is becoming more prevalent." --highlight

# Or with the dedicated script
python highlight.py "The utilize of technology is becoming more prevalent."

# With more suggestions
python flow.py "Your text" --highlight --highlight-suggestions 5

# From a file
python flow.py --file draft.txt --highlight
```

**Output Example:**
```
📝 'utilize'
   Entropy: 5.60 bits | Rank: #8131 | Log-prob: -16.83
   Flagged: high uncertainty (H≥4.0), low rank (rank≥50)
   Top replacements:
   ✓ 1. use            → ΔLL= +5.20 | sim=0.967 | p= -1.20
   ✓ 2. adoption       → ΔLL= +3.40 | sim=0.952 | p= -2.10
     3. implementation → ΔLL= +0.80 | sim=0.948 | p= -3.50
```

**Benefits:**
- ✅ Fast identification of problem areas
- ✅ Shows top suggestions with quality metrics
- ✅ No automatic changes made
- ✅ Easy to understand output

## 2. Show Candidates Mode (Default)

**When to use:** You want to see all possible replacements for every word with detailed metrics.

```bash
# Default behavior - shows top 5 sentence-level modifications
python flow.py "Your text here"

# Show more modifications
python flow.py "Your text" --show-candidates 10
```

**Output Example:**
```
Top 5 most promising modifications:
Legend: ✓ = passes thresholds (ΔLL ≥ 1.5, sim ≥ 0.95)

✓ 1. 'utilize' → 'use'
   Modified: The use of technology is becoming more prevalent.
   Quality: 18.45 | ΔLL: +5.20 | sim: 0.967
   Original entropy: 5.60 bits | rank: #8131
```

**Benefits:**
- ✅ Comprehensive view of all possible improvements
- ✅ Ranked by quality score
- ✅ Shows modified sentence preview

## 3. Apply Edits Mode (Automatic)

**When to use:** You trust the system and want automatic improvements.

```bash
# Apply edits automatically
python flow.py "The utilize of technology is important." --apply-edits

# Process a file
python flow.py --file input.txt --output output.txt --apply-edits
```

**Output Example:**
```
ORIGINAL TEXT:
The utilize of technology is becoming more prevalent.

REFINED TEXT:
The use of technology is becoming more prevalent.

Sentence 1: 1 edit(s)
  'utilize' → 'use'
```

**Benefits:**
- ✅ Fast batch processing
- ✅ Automatic improvements
- ✅ Shows what changed

## 4. Interactive Mode (Manual Approval)

**When to use:** You want control over each change.

```bash
# Interactive approval of each edit
python flow.py "Your text here" --interactive
```

**Output Example:**
```
============================================================
Proposed edit:
  Original: 'utilize'
  Replacement: 'use'
  Reason: high uncertainty (H=5.6 bits); improves fluency (+5.20 PLL); preserves meaning (0.967 sim)

Top alternatives:
  1. use (ΔLL=+5.20)
  2. adoption (ΔLL=+3.40)
  3. implementation (ΔLL=+0.80)
============================================================
Accept this edit? (y/n/1-3 for alternative): 
```

**Benefits:**
- ✅ Full control over changes
- ✅ Can choose alternative suggestions
- ✅ See reasoning for each edit

## Real-World Workflows

### Workflow 1: Quick Draft Check

```bash
# Step 1: Quick scan for issues
python flow.py "Your draft text..." --highlight

# Step 2: Review flagged words manually
# Step 3: Make changes yourself
```

### Workflow 2: Important Document

```bash
# Step 1: See all possible improvements
python flow.py --file important_doc.txt

# Step 2: Apply with manual approval
python flow.py --file important_doc.txt --interactive

# Step 3: Save to new file
python flow.py --file important_doc.txt --output improved_doc.txt --interactive
```

### Workflow 3: Batch Processing

```bash
# Process multiple files automatically
for file in drafts/*.txt; do
    python flow.py --file "$file" --output "refined_$file" --apply-edits
done
```

### Workflow 4: Sensitivity Tuning

```bash
# Start conservative (only obvious issues)
python flow.py "Your text" --highlight --min-entropy 5.0

# Try balanced (default)
python flow.py "Your text" --highlight --min-entropy 4.0

# Try aggressive (catch more potential issues)
python flow.py "Your text" --highlight --min-entropy 3.5
```

## Configuration Options

### Model Selection

```bash
# Fast (roberta-base) - good for drafts
python flow.py "Your text" --model roberta-base --highlight

# Accurate (roberta-large) - good for important text
python flow.py "Your text" --model roberta-large --highlight
```

### Threshold Tuning

```bash
# More aggressive detection
python flow.py "Your text" --min-entropy 3.5 --max-rank 100 --highlight

# More conservative
python flow.py "Your text" --min-entropy 5.0 --max-rank 20 --highlight

# Lower fluency requirements
python flow.py "Your text" --min-pll-gain 1.0 --highlight

# Higher similarity requirements
python flow.py "Your text" --min-similarity 0.98 --highlight
```

### Advanced Options

```bash
# Enable NLI semantic checking (slower but safer)
python flow.py "Your text" --use-nli --highlight

# Allow more edits per sentence
python flow.py "Your text" --max-edits 5 --apply-edits

# Adjust PLL window size
python flow.py "Your text" --pll-window 7 --highlight

# Consider more candidates
python flow.py "Your text" --top-k 30 --highlight
```

## Python API Examples

### Example 1: Highlight Mode

```python
from config import FlowConfig
from refinement_pipeline import RefinementPipeline

config = FlowConfig(roberta_model="roberta-base")
pipeline = RefinementPipeline(config)

text = "The utilize of machine learning is revolutionary."
pipeline.highlight_clunky_words(text, show_top_replacements=3)
```

### Example 2: Get Refinement Result

```python
from config import FlowConfig
from refinement_pipeline import RefinementPipeline

config = FlowConfig(roberta_model="roberta-base")
pipeline = RefinementPipeline(config)

text = "The utilize of technology is important."
result = pipeline.refine_sentence(text)

print(f"Original: {result.original}")
print(f"Refined: {result.refined}")

for edit in result.edits:
    print(f"Changed '{edit.original_word}' to '{edit.replacement}'")
    print(f"Reason: {edit.reason}")
```

### Example 3: Custom Configuration

```python
from config import FlowConfig
from refinement_pipeline import RefinementPipeline

# Custom configuration
config = FlowConfig(
    roberta_model="roberta-large",
    min_entropy=3.5,              # More aggressive
    min_pll_gain=1.0,             # More lenient
    min_sbert_cosine=0.97,        # Stricter similarity
    max_edits_per_sentence=3,     # Allow more edits
    use_nli_check=True            # Enable NLI checking
)

pipeline = RefinementPipeline(config)
text = "Your text here"
refined = pipeline.refine_text(text)
```

## Tips and Best Practices

1. **Start with Highlight Mode** - Get a quick overview before making changes
2. **Use Base Model for Drafts** - Save time with roberta-base for initial drafts
3. **Use Large Model for Important Text** - Use roberta-large for final versions
4. **Focus on ✓ Suggestions** - These pass all quality thresholds
5. **Trust Your Judgment** - The model suggests, you decide
6. **Tune Thresholds** - Adjust sensitivity based on your writing style
7. **Use Interactive Mode** - For important documents where you want control
8. **Process Files** - Use `--file` and `--output` for document workflows

## Common Questions

**Q: Which mode should I start with?**
A: Start with `--highlight` to quickly identify potential issues.

**Q: How do I know if a suggestion is good?**
A: Look for the ✓ mark - it means the suggestion passes all quality checks.

**Q: Can I adjust how sensitive it is?**
A: Yes! Use `--min-entropy` (lower = more sensitive) and `--min-pll-gain` (lower = more lenient).

**Q: Will it change my writing style?**
A: No - it only suggests improvements for words that score poorly in context. You always have final control.

**Q: Is it safe to use --apply-edits?**
A: The thresholds are conservative, but review the output. For important text, use `--interactive` instead.

