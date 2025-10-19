# Flow - Bidirectional Text Refinement using RoBERTa

Flow is a sophisticated text refinement system that uses RoBERTa's bidirectional context understanding to identify and improve "clunky" words in sentences while preserving semantic meaning and linguistic correctness.

## 🧠 Core Concept

Flow scores each word by masking its subword span and measuring RoBERTa's surprise (entropy) at the original token. High-entropy positions indicate "clunky" words that can be improved. The system then:

1. **Scores** words using bidirectional masked language modeling
2. **Generates** candidates from RoBERTa's fill-mask distribution  
3. **Filters** candidates using linguistic constraints (POS, morphology)
4. **Re-ranks** candidates by local fluency improvement (PLL gain)
5. **Validates** semantic preservation using Sentence-BERT similarity

## 🏗️ Architecture

- **Tokenizer + Aligner**: Maps between characters, words, and subword pieces
- **Bidirectional Scorer**: Computes entropy and pseudo-log-likelihood (PLL) 
- **Candidate Generator**: Generates replacements from masked predictions
- **Semantic Checker**: Ensures meaning preservation via SBERT + optional NLI
- **Linguistic Constraints**: Enforces POS/morphology agreement via spaCy
- **Refinement Pipeline**: Orchestrates greedy left-to-right editing

## 🚀 Installation

### Option 1: Using uv (Recommended - Fast!)

```bash
# Clone the repository
git clone <your-repo-url>
cd flow

# Create virtual environment with uv
uv venv venv

# Activate and install dependencies
source venv/bin/activate
uv pip install -r requirements.txt

# Install spaCy model
uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

# Test installation
python test_basic.py
```

### Option 2: Using pip

```bash
# Clone the repository
git clone <your-repo-url>
cd flow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Test installation
python test_basic.py
```

### Quick Start Script

```bash
# Use the activation helper
source activate.sh
```

## 📖 Usage

### Highlight Mode (Quick Analysis) 🆕

The fastest way to identify words that need editing:

```bash
# Highlight mode - shows words most likely to need editing
python flow.py "The utilize of technology is becoming more prevalent." --highlight

# Or use the dedicated script
python highlight.py "The utilize of technology is becoming more prevalent."

# Show more replacement suggestions per word
python flow.py "Your text" --highlight --highlight-suggestions 5

# Process a file
python flow.py --file input.txt --highlight
```

**Highlight mode output:**
- 📝 Marks each word that likely needs editing
- Shows entropy (uncertainty), rank, and log-probability scores
- Provides top 3 replacement suggestions with fluency gain (ΔLL) and similarity metrics
- ✓ indicates replacements that pass all quality thresholds

### Command Line Interface

```bash
# Basic usage - shows top 5 candidates for each word (default behavior)
python flow.py "Thank you for your attention to this matter"

# Apply edits automatically instead of showing candidates
python flow.py "Your text" --apply-edits

# Show more or fewer candidates
python flow.py "Your text" --show-candidates 10

# Interactive mode (confirm each edit)
python flow.py "Your text here" --interactive

# Use faster model
python flow.py "Your text" --model roberta-base

# Adjust sensitivity
python flow.py "Your text" --min-entropy 3.5 --min-pll-gain 1.0

# Enable NLI checking for extra semantic safety
python flow.py "Your text" --use-nli

# Process file
python flow.py --file input.txt --output refined.txt
```

### Understanding the Output

By default, Flow shows the **top 5 candidate replacements** for each word with:
- **Entropy** (H): How uncertain RoBERTa is about this position (higher = more "clunky")
- **Rank**: Where the original word ranks in RoBERTa's predictions
- **ΔLL** (Delta Log-Likelihood): Fluency improvement (positive = better, negative = worse)
- **sim**: Semantic similarity with original sentence (0-1, higher = more similar)
- **p**: Log probability of the candidate in masked position
- **✓**: Indicates candidate passes both fluency (ΔLL ≥ threshold) and similarity (sim ≥ threshold) checks

Example output:
```
📝 'utilize'
   Entropy: 5.60 bits | Rank: #8131 | Log-prob: -16.83
   Top replacements:
   ✓ 1. adoption       → ΔLL= +7.87 | sim=0.962 | p= -1.34
     2. use            → ΔLL= -2.10 | sim=0.924 | p= -2.76
```

### Python API

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