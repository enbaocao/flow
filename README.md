
# Flow
*make sentences flow better!*

we use roberta's bidirectional mlm to find awkward words in the middles of sentences and find more fluid alternatives.

---

### Web Interface

```bash
./start.sh
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