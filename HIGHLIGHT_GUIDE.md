# Flow Highlight Mode - User Guide

## What is Highlight Mode?

Highlight Mode is a quick analysis feature that identifies words in your text that are most likely to need editing, without automatically applying any changes. Think of it as a "spell-check" for awkward or clunky word choices.

## How It Works

Flow uses RoBERTa's bidirectional language model to:
1. **Score each word** based on how uncertain the model is about that position (entropy)
2. **Identify "clunky" words** that score above the threshold
3. **Show replacement suggestions** with quality metrics
4. **Highlight which suggestions** pass all quality checks (✓)

## Quick Start

### Basic Usage

```bash
# Analyze text from command line
python flow.py "Your text here" --highlight

# Or use the dedicated script
python highlight.py "Your text here"

# Analyze a file
python flow.py --file document.txt --highlight
```

### Example

```bash
python flow.py "The utilize of advanced algorithms has revolutionized data processing." --highlight
```

**Output:**
```
======================================================================
HIGHLIGHTED TEXT ANALYSIS
======================================================================
Original text:
The utilize of advanced algorithms has revolutionized data processing.

======================================================================
Words likely to need editing:
======================================================================

📝 'utilize'
   Entropy: 5.60 bits | Rank: #8131 | Log-prob: -16.83
   Flagged: high uncertainty (H≥4.0), low rank (rank≥50)
   Top replacements:
   ✓ 1. use            → ΔLL= +5.20 | sim=0.967 | p= -1.20
   ✓ 2. adoption       → ΔLL= +3.40 | sim=0.952 | p= -2.10
     3. implementation → ΔLL= +0.80 | sim=0.948 | p= -3.50

======================================================================
Summary: 1 word(s) highlighted across 1 sentence(s)

Legend:
  • Entropy (H): Higher = more uncertain (threshold: 4.0 bits)
  • Rank: Position in probability distribution (threshold: 50)
  • ΔLL: Change in log-likelihood (fluency gain, threshold: 1.5)
  • sim: Semantic similarity (threshold: 0.95)
  • p: Log probability of replacement candidate
  • ✓: Candidate passes all thresholds
======================================================================
```

## Understanding the Metrics

### Word Scores

- **Entropy (H)**: Measures uncertainty. Higher values (≥4.0 bits) indicate the model is "surprised" by the word choice, suggesting it might be awkward or unusual.

- **Rank**: Where the original word ranks in the model's predictions. A rank of 8131 means 8130 other words were more probable. Low ranks (≥50) suggest the word is unexpected.

- **Log-prob**: The log probability of the original word. More negative values = less probable.

### Replacement Metrics

- **ΔLL (Delta Log-Likelihood)**: Measures fluency improvement. Positive values mean the replacement makes the sentence flow better. Threshold: ≥1.5.

- **sim (Similarity)**: Semantic similarity between original and modified sentence. Values close to 1.0 mean the meaning is preserved. Threshold: ≥0.95.

- **p (Candidate probability)**: How probable the replacement is in that position. Less negative = more natural.

- **✓ (Check mark)**: Indicates the replacement passes both fluency (ΔLL ≥ 1.5) and similarity (sim ≥ 0.95) thresholds.

## Advanced Options

### Show More Suggestions

```bash
# Show top 5 replacements per word instead of 3
python flow.py "Your text" --highlight --highlight-suggestions 5
```

### Adjust Sensitivity

```bash
# More aggressive (catches more potential issues)
python flow.py "Your text" --highlight --min-entropy 3.5

# More conservative (only obvious problems)
python flow.py "Your text" --highlight --min-entropy 5.0
```

### Use Different Models

```bash
# Faster analysis with base model
python flow.py "Your text" --highlight --model roberta-base

# More accurate with large model (slower)
python flow.py "Your text" --highlight --model roberta-large
```

### Process Multiple Paragraphs

The highlight mode automatically handles multi-sentence text:

```bash
python flow.py "First sentence here. Second sentence here. Third sentence here." --highlight
```

## Common Use Cases

### 1. Quick Draft Review

Copy-paste a paragraph to identify areas that might need refinement:

```bash
python highlight.py "Your draft paragraph here..."
```

### 2. Email Polish

Check an important email before sending:

```bash
python flow.py --file email_draft.txt --highlight
```

### 3. Academic Writing

Identify potentially awkward phrases in academic text:

```bash
python flow.py "Your academic text..." --highlight --min-pll-gain 2.0
```

### 4. Batch Analysis

Process multiple files:

```bash
for file in drafts/*.txt; do
    echo "Analyzing $file"
    python flow.py --file "$file" --highlight
done
```

## Python API

Use highlight mode programmatically:

```python
from config import FlowConfig
from refinement_pipeline import RefinementPipeline

# Configure
config = FlowConfig(
    roberta_model="roberta-base",
    min_entropy=4.0,
    min_pll_gain=1.5
)

# Initialize
pipeline = RefinementPipeline(config)

# Analyze text
text = "Your text here"
pipeline.highlight_clunky_words(text, show_top_replacements=3)
```

## Tips for Best Results

1. **Start with default settings** - The thresholds are tuned for good balance
2. **Use base model for quick checks** - Save the large model for important text
3. **Focus on ✓ suggestions** - These pass all quality checks
4. **Context matters** - Consider your audience and writing style
5. **Use as a guide** - The model helps identify potential issues, but you make the final call

## Workflow: Highlight → Review → Apply

Recommended workflow:

```bash
# Step 1: Identify issues
python flow.py "Your text" --highlight

# Step 2: Review the suggestions manually

# Step 3: Apply edits automatically (optional)
python flow.py "Your text" --apply-edits

# OR Step 3: Apply edits interactively
python flow.py "Your text" --interactive
```

## Troubleshooting

### No words highlighted

This is good! It means your text doesn't have obvious issues according to the model. You can:
- Lower the thresholds: `--min-entropy 3.5`
- Check with a different model: `--model roberta-large`

### Too many words highlighted

The sensitivity might be too high. Try:
- Raising the thresholds: `--min-entropy 5.0`
- Focus on suggestions with ✓ marks

### Slow performance

- Use `roberta-base` instead of `roberta-large`
- Process shorter text segments
- Consider using GPU: `--device cuda`

## Next Steps

After using highlight mode, you can:
1. Manually edit based on suggestions
2. Use `--apply-edits` to automatically apply changes
3. Use `--interactive` mode to approve each change
4. Use `--show-candidates` to see all possible replacements

## Learn More

- See `README.md` for full documentation
- Run `python flow.py --help` for all options
- Check `example.py` for code examples

