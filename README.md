<div align="center">

# 🌊 Flow

### AI-Powered Text Refinement Using RoBERTa

*Identify and improve clunky words while preserving meaning*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)

[Quick Start](#-quick-start) • [Demo](#-demo) • [How It Works](#-how-it-works) • [API](#-python-api)

</div>

---

## 🎯 What is Flow?

Flow uses **RoBERTa's bidirectional masked language modeling** to identify awkward or "clunky" words in your text and suggest natural-sounding alternatives. Unlike traditional grammar checkers, Flow understands context and preserves your intended meaning.

## ✨ Key Features

- 🎯 **Smart Word Scoring** - Uses entropy and probability ranking to flag problematic words
- 🔄 **Context-Aware Replacements** - Generates alternatives that fit naturally in context
- 🛡️ **Meaning Preservation** - Ensures semantic similarity with Sentence-BERT
- 📊 **Transparent Metrics** - See fluency gains (ΔLL) and similarity scores for every suggestion
- ⚡ **Fast & Lightweight** - Uses `roberta-base` by default for quick responses
- 🎨 **Web Interface** - Beautiful Next.js frontend for interactive text refinement

---

## 🚀 Quick Start

### CLI Usage

```bash
# Clone and setup
git clone https://github.com/enbaocao/flow.git
cd flow
source activate.sh

# Highlight problematic words
python flow.py "The utilize of technology is becoming more prevalent." --highlight

# Apply automatic edits
python flow.py "Your text here" --apply-edits

# Interactive mode (approve each edit)
python flow.py "Your text here" --interactive
```

### Web Interface

```bash
# Start the full-stack app (API + Frontend)
./start.sh
```

Then open **http://localhost:3000** in your browser.

---

## 📦 Installation

<details>
<summary><b>Using uv (Recommended)</b></summary>

```bash
# Create virtual environment
uv venv venv
source venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Install spaCy model
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

</details>

<details>
<summary><b>Using pip</b></summary>

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

</details>

---

## 💡 Demo

### Input
```
The utilize of advanced algorithms has revolutionized data processing.
```

### Highlight Mode Output
```
📝 'utilize'
   Entropy: 5.60 bits | Rank: #8131 | Log-prob: -16.83
   
   Top replacements:
   ✓ 1. use            → ΔLL= +7.87 | sim=0.962 | p= -1.34
     2. adoption       → ΔLL= +4.23 | sim=0.945 | p= -2.10
     3. implementation → ΔLL= +2.15 | sim=0.931 | p= -3.45

✓ = passes fluency & similarity thresholds
```

### Refined Output
```
The use of advanced algorithms has revolutionized data processing.
```

---

## 🧠 Core Concept

Flow scores each word by masking it and measuring RoBERTa's uncertainty. High entropy = clunky word. The pipeline then:

1. 🎯 **Scores** words using bidirectional masked language modeling
2. 🔮 **Generates** candidates from RoBERTa's fill-mask predictions
3. 🔍 **Filters** using linguistic constraints (POS, morphology)
4. 📈 **Re-ranks** by fluency improvement (PLL gain)
5. ✅ **Validates** semantic preservation with Sentence-BERT

<details>
<summary><b>Architecture Overview</b></summary>

- **Tokenizer + Aligner** - Maps characters ↔ words ↔ subword tokens
- **Bidirectional Scorer** - Computes entropy & pseudo-log-likelihood (PLL)
- **Candidate Generator** - Generates replacements from masked predictions
- **Semantic Checker** - SBERT similarity + optional NLI entailment
- **Linguistic Constraints** - POS/morphology agreement via spaCy
- **Refinement Pipeline** - Greedy left-to-right editing orchestration

</details>

---

## 📖 Usage

### 🎨 Highlight Mode (Recommended)

Quickly identify problematic words without making changes:

```bash
# Basic highlight
python flow.py "The utilize of technology is becoming more prevalent." --highlight

# Show more suggestions per word
python flow.py "Your text" --highlight --highlight-suggestions 5

# Process a file
python flow.py --file input.txt --highlight
```

**Output includes:**
- 📝 Flagged words with entropy, rank, and log-probability
- Top N replacement suggestions ranked by fluency
- ΔLL (fluency gain) and similarity scores
- ✓ indicates candidates passing quality thresholds

### ⚙️ Edit Mode

Apply automatic refinements:

```bash
# Auto-apply best edits
python flow.py "Your text here" --apply-edits

# Interactive approval
python flow.py "Your text here" --interactive

# Process file and save output
python flow.py --file input.txt --output refined.txt --apply-edits
```

### 🛠️ Advanced Options

```bash
# Use larger model for better accuracy
python flow.py "text" --model roberta-large --highlight

# Adjust sensitivity (lower = more aggressive)
python flow.py "text" --min-entropy 3.5 --min-pll-gain 1.0

# Enable NLI for stricter semantic checking
python flow.py "text" --use-nli --apply-edits

# Show candidate analysis (default behavior)
python flow.py "text" --show-candidates 10
```

---

## 🐍 Python API

```python
from config import FlowConfig
from refinement_pipeline import RefinementPipeline

# Create configuration
config = FlowConfig(
    roberta_model="roberta-base",
    min_entropy=4.0,
    min_pll_gain=2.0,
    min_sbert_cosine=0.97
)

# Initialize pipeline
pipeline = RefinementPipeline(config)

# Highlight mode - identify words that need editing
text = "The utilize of technology is becoming more prevalent."
pipeline.highlight_clunky_words(text, show_top_replacements=3)
# Shows: 'utilize' with top replacement suggestions and metrics

# Or refine text (apply edits)
refined = pipeline.refine_text(text)
print(refined)
# Output: "The use of technology is becoming more prevalent."
```

## ⚙️ Configuration

### Key Thresholds (Sane Defaults)

```python
# Scoring thresholds
min_entropy = 4.0        # bits - flag high-entropy positions  
max_original_rank = 50   # flag if original word ranks poorly

# Re-ranking thresholds  
min_pll_gain = 2.0       # log-units improvement required
min_sbert_cosine = 0.97  # semantic similarity threshold
pll_window_size = 5      # tokens ±5 around edit

# Safety limits
max_edits_per_sentence = 2  # conservative edit budget
```

### Model Options

- **RoBERTa Model**: `roberta-base` (faster) or `roberta-large` (more accurate)
- **SBERT Model**: `all-MiniLM-L6-v2` (fast and effective)
- **NLI Model**: `roberta-large-mnli` (optional entailment checking)
- **spaCy Model**: `en_core_web_sm` (POS tagging and morphology)

## 🔬 How It Works

### 1. Word Scoring
For each word, Flow:
- Masks the word's subword span with `<mask>` tokens
- Computes entropy: `H = -Σ p log p` (measures uncertainty)
- Gets original word's probability and rank in distribution
- For multi-piece words, uses pseudo-log-likelihood (PLL)

### 2. Candidate Generation
- Takes top-k predictions from masked position
- Applies basic filtering (no punctuation, proper length, etc.)  
- Preserves capitalization style of original word

### 3. Linguistic Filtering
- Ensures POS tag compatibility (noun→noun, verb→verb)
- Matches morphological features (singular→singular, past→past)
- Filters out proper nouns and numbers as replacements

### 4. Semantic Validation
- Computes Sentence-BERT cosine similarity
- Optional NLI entailment checking with RoBERTa-MNLI
- Rejects candidates that drift in meaning

### 5. Fluency Re-ranking
- Computes windowed PLL around edit position
- Only accepts edits that improve local fluency by threshold
- Uses "word-l2r" PLL method for robust multi-piece scoring

## 📊 Example Results

```
Original: "The utilize of advanced algorithms has revolutionized data processing."
Refined:  "The use of advanced algorithms has revolutionized data processing."

Edit: 'utilize' → 'use'
Reason: high uncertainty (H=4.7 bits); improves fluency (+2.1 PLL); preserves meaning (0.967 sim)
```

## 🎛️ CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--model` | RoBERTa model (`roberta-base`/`roberta-large`) | `roberta-base` |
| `--interactive` | Interactive mode with user approval | `False` |
| `--min-entropy` | Entropy threshold for flagging words | `4.0` |
| `--min-pll-gain` | PLL improvement required | `2.0` |
| `--min-similarity` | SBERT similarity threshold | `0.97` |
| `--use-nli` | Enable NLI entailment checking | `False` |
| `--max-edits` | Max edits per sentence | `2` |
| `--device` | Device (`cpu`/`cuda`) | `cpu` |

## 🔧 Advanced Usage

### Custom Configuration

```python
config = FlowConfig(
    roberta_model="roberta-large",  # Slower but more exhaustive
    min_entropy=3.5,                 # More aggressive
    min_pll_gain=1.0,                # More lenient
    use_nli_check=True,            # Extra semantic safety
    max_edits_per_sentence=3       # Allow more edits
)
```

### Batch Processing

```python
sentences = [
    "The utilize of technology is important.",
    "We should definately consider this approach.",
    "The data was analyzed by the research team."
]

for sentence in sentences:
    result = pipeline.refine_sentence(sentence)
    print(f"Original: {result.original}")
    print(f"Refined:  {result.refined}")
    for edit in result.edits:
        print(f"  Edit: '{edit.original_word}' → '{edit.replacement}'")
    print()
```

## 🧪 Technical Details

### Multi-piece Word Handling
- Uses pseudo-log-likelihood (PLL) for scoring multi-subword tokens
- Implements "word-l2r" method: mask current piece + remaining pieces to the right
- Generates single-token replacements for simplicity (often effective)

### Speed vs Accuracy Tradeoffs
- `roberta-base` (default): lightweight and quick for interactive use
- `roberta-large`: ~4× slower but can surface rarer alternatives
- Batch multiple positions in one forward pass for efficiency
- Pre-filter candidates before expensive PLL computation

### Linguistic Safety
- spaCy POS tagging and morphological analysis
- Preserves number agreement (singular/plural)
- Maintains verb tense and mood
- Avoids suggesting proper nouns or numbers

## 🤝 Contributing

Contributions welcome! Key areas for improvement:
- Multi-token span edits (currently single words only)
- Better morphological constraint handling
- Support for non-English languages
- Performance optimizations

## 📚 References

- Salazar et al. (2020): "Masked Language Model Scoring"  
- Wang & Cho (2019): "BERT has a Mouth, and It Must Speak"
- Malmi et al. (2019): "Encode, Tag, Realize: High-Precision Text Editing"

## 📄 License

MIT License - see LICENSE file for details.