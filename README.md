
# Flow
*make sentences flow better!*

we use roberta's bidirectional mlm to find awkward words in the middles of sentences and find more fluid alternatives.

---

## CLI Usage

```bash
# Clone and setup
git clone https://github.com/enbaocao/flow.git
cd flow
source scripts/activate.sh

# Highlight problematic words
python -m backend.flow "The utilize of technology is becoming more prevalent." --highlight

# Apply automatic edits
python -m backend.flow "Your text here" --apply-edits

# Interactive mode (approve each edit)
python -m backend.flow "Your text here" --interactive
```

---

### Web Interface

```bash
./scripts/start.sh
```

---

## Custom Configuration

```python
config = FlowConfig(
    roberta_model="roberta-large",   # more accuracy, slower
    min_entropy=3.5,                 # aggressive flagging
    min_pll_gain=1.0,                # lenient edits
    use_nli_check=True,              # safe
    device="cuda"                    # gpu
)
```