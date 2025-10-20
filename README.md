<div align="center">

# Flow

*make sentences flow better!*

</div>

---

## What is Flow?

Flow uses **RoBERTa's bidirectional masked language modeling** to identify awkward or "clunky" words in your text and suggest natural-sounding alternatives. Unlike traditional grammar checkers, Flow understands context and preserves your intended meaning.

---

## CLI Usage

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

## Custom Configuration

```python
config = FlowConfig(
    roberta_model="roberta-large",  # More accurate, slower
    min_entropy=3.5,                 # More aggressive flagging
    min_pll_gain=1.0,                # More lenient edits
    use_nli_check=True,              # Extra semantic safety
    device="cuda"                    # GPU acceleration
)
```