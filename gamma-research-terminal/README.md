# Γ Gamma Lab — Order-Flow Research Terminal

**Causal research terminal for ES/NQ futures.** Combines tick-level order-flow analysis with point-in-time options gamma exposure to test location-based hypotheses under walk-forward evaluation.

> Historical research only. No live feed. No order routing. No profitability claims. Local-first by design.

---

## What it does

Gamma Lab lets you:

1. **Import futures tick data** — Canonical CSV/Parquet, NinjaTrader tick text, and Databento trades CSV.
2. **Import options snapshots** — Strike-level OI, quotes, and explicit publication timestamps for point-in-time analysis.
3. **Classify trades** — Causal quote-side inference for unknown aggressor trades, embedded-quote extraction.
4. **Build footprint charts** — 60-second bars with delta, volume, and classified-fraction metrics.
5. **Compute gamma Greeks** — Black-76 model via QuantLib, with IV solving per contract, gamma-dollar concentration.
6. **Test four registered hypotheses** — Price baseline, gamma location, footprint, and gamma + footprint — under identical execution assumptions.
7. **Walk-forward evaluation** — Rolling training/out-of-sample splits, holdout session reserved until explicit consent.
8. **Execution simulation** — Latency, slippage, quote aging, session loss halts, integer contract sizing, stop/target logic.
9. **Stress scenarios** — Replay signals under varying cost/latency assumptions without retuning.
10. **Trade journal** — Persistent SQLite trial registry with source hashes, engine versioning, and exportable audit bundles.

Every screen enforces point-in-time awareness — you cannot borrow information from the future.

---

## Screens

| Screen | Purpose |
|---|---|
| **Data workspace** | Import, audit, and select source files. Load synthetic tutorial. |
| **Options map** | Gamma-dollar concentration bars, exclusion audit, signed-gamma scenarios. |
| **Synchronized replay** | Cursor-driven replay with footprint, quote book, and OFI diagnostics. |
| **Research** | Walk-forward comparison, holdout evaluation, stress testing, deflated Sharpe. |
| **Trade journal** | Persistent trial registry with configuration hashes and exportable audit zip. |

---

## Quick start

### Requirements

- Python 3.11+
- [QuantLib](https://www.quantlib.org/) (installed automatically via pip)

### Install & run

```bash
git clone https://github.com/savastanomngm-cyber/AstraSFD.git
cd AstraSFD/gamma-research-terminal

# Create venv and install
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Launch the terminal
python3 launch.py
```

Open http://localhost:8501 in your browser.

### Docker

```bash
docker compose up --build
```

### Load the tutorial

Click **"Explore with synthetic data"** → **"Load synthetic tutorial"** in the Data workspace. This generates a 6-session deterministic synthetic dataset so you can explore every screen without importing real market data. All synthetic data is clearly labeled and not presented as historical evidence.

---

## Importing your own data

### Supported formats

| Format | Streams | Notes |
|---|---|---|
| **Canonical CSV/Parquet** | trade, quote, bid, ask, options | Schema documented in-app; download templates from Data workspace. |
| **NinjaTrader tick text** | Last, Bid, Ask | 3-field tick or 5-field Last tick-replay. Bars/Market Replay unsupported. |
| **Databento trades CSV** | trades only | Pretty timestamps, decimal prices, single resolved instrument. |

### Options data requirements

- Explicit Open Interest publication timestamps (`oi_available_at`) — OI is unusable before its publication instant.
- European-style only (American contracts are excluded from Black-76 analytics).
- Individual contract futures (ESU6, NQU6), not continuous symbols.

### Limits

- 100 MB / 2 million records per import.
- Overlapping sources for the same contract/stream are rejected, not silently deduplicated.

---

## Architecture

```
gamma-research-terminal/
├── launch.py              # Streamlit launcher with venv bootstrapping
├── terminal.py            # Main Streamlit app entry point
├── gamma_lab/
│   ├── data_screen.py     # Import UI & source management
│   ├── evaluation.py      # Walk-forward experiment orchestration
│   ├── execution.py       # Quote-driven trade simulation engine
│   ├── importers.py       # Canonical, NinjaTrader, Databento parsers
│   ├── models.py          # Contract specs, RunConfig, session_id
│   ├── options.py         # Black-76, Greeks, snapshot, concentration
│   ├── orderflow.py       # Classification, quote book, footprint, OFI
│   ├── replay_screen.py   # Cursor-driven replay & options map UI
│   ├── research.py        # Walk-forward logic, signal generation
│   ├── research_screen.py # Research, journal, and stress UI
│   ├── setups.py          # Gamma/round-number/close zone detection
│   ├── statistics.py      # Summaries, block intervals, deflated Sharpe
│   ├── storage.py         # SQLite + Parquet + DuckDB persistence
│   ├── tutorial.py        # Seeded synthetic data generator
│   └── visuals.py         # Plotly charts & Streamlit styling
├── tests/
│   ├── test_terminal.py   # Streamlit integration tests
│   └── test_invariants.py # Engine invariants, property tests
├── data/                  # Local storage (gitignored)
│   ├── registry.sqlite    # Source, study, run, and exposure tables
│   ├── sources/           # Immutable original.bin + Parquet partitions
│   └── runs/              # Per-run Parquet artifacts
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── LICENSE
```

### Key design decisions

- **Point-in-time everywhere.** `known_rows()` clips data at the cursor. Signals never look ahead. Holdout data is cryptographically invisible to training.
- **Immutable sources.** Every imported file is SHA-256 hashed. Parquet partitions are deduplicated by digest. Engine files are hashed and recorded in every trial.
- **No silent decisions.** Overlapping sources are rejected. Off-tick prices are rejected. Ambiguous same-timestamp quotes are invalidated. Every exclusion has an auditable reason.
- **DuckDB for queries, Parquet for storage, SQLite for the registry.** No server process required.

---

## Hypotheses tested

All four variants share the same execution engine and configuration:

1. **Price baseline** — Round-number zones (±12.5 points off 25-point increments).
2. **Gamma location** — Point-in-time gamma-dollar concentration peak (requires options data).
3. **Footprint** — Delta-ratio rejection signals, independent of location zones.
4. **Gamma + footprint** — Combined: zone proximity AND footprint pressure.

Each walk-forward fold trains on the preceding N sessions, selects a delta threshold from {0.20, 0.35} by training P&L, and applies the chosen threshold to the test session. The final session is always reserved and only opened with explicit consent.

---

## Testing

```bash
python3 -m pytest tests/ -q
```

37 tests covering:
- Streamlit screen integration (empty workspace, blocked research, tutorial workflow, journal persistence)
- Engine invariants (footprint reconciliation, stale-quote blocking, latency enforcement, stop slippage, OFI requirements)
- Data integrity (roundtrip immutability, overlap rejection, holdout isolation, forward-completeness)
- Property-based testing (footprint volume/delta reconciliation via Hypothesis)
- DST session boundaries, off-tick rejection, canonical validation

---

## Scope & limitations

- **Research tool, not a trading system.** No live data, no order routing, no broker integration.
- **ES and NQ futures only.** Individual contracts (ESU6, NQU6); continuous symbols rejected.
- **60-second bars only.** Bar size is not configurable in this release.
- **Black-76 only.** No stochastic vol, no early-exercise models. No total-market dealer gamma claims.
- **Single-contract analysis.** No spread or multi-leg strategies.
- **No automatic data downloads.** Market-data entitlements remain your responsibility.

---

## License

MIT — see [LICENSE](./LICENSE).
