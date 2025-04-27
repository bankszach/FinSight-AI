# AI-Powered Personal Finance Analyzer

A next-generation personal finance tool that leverages Large Language Models (LLMs) for intelligent transaction analysis and financial insights.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure OpenAI API:
```bash
cp .env.example .env
# Edit .env with your API key
```

3. Place financial statements in `data/raw/`

4. Run analysis:
```bash
python -m src.cli
```

## Core Features

### 1. AI-Powered Transaction Processing
- **Smart Categorization**: Multi-layer categorization system
  - Rule-based matching (configurable in config.yml)
  - Fuzzy matching for similar descriptions
  - LLM-powered categorization for complex cases
- **Natural Language Understanding**: LLM interprets transaction descriptions
- **Context-Aware Analysis**: AI considers transaction patterns and relationships

### 2. Intelligent Financial Analysis
- **Automated Insights Generation**
  - Monthly spending patterns
  - Category breakdowns
  - Cash flow analysis
  - Large transaction identification
- **Predictive Analysis**
  - Spending trend detection
  - Anomaly identification
  - Future cash flow projections

## Project Structure
```
.
├── data/                    # Data storage
├── src/                     # Source code
├── docs/                    # Documentation
├── tests/                   # Test suite
├── notebooks/               # Jupyter notebooks
└── config.yml               # Configuration
```

## Documentation

For detailed technical documentation, see the `docs/` directory:
- [Development Guide](docs/development.md)
- [AI Integration](docs/ai_integration.md)
- [Data Pipeline](docs/data_pipeline.md)
- [API Reference](docs/api_reference.md)

## Configuration

Edit `config.yml` to:
- Define category mapping rules
- Set currency preferences
- Configure date ranges
- Adjust analysis parameters

Edit `.env` to configure OpenAI API:
- OPENAI_API_KEY: Project-scoped API key
- OPENAI_API_BASE: API endpoint
- OPENAI_MODEL: Model selection
- OPENAI_TEMP: Output determinism

## Contributing

This project welcomes contributions focused on:
- AI/ML model improvements
- Natural language processing
- Financial analysis algorithms
- Integration capabilities

See [Contributing Guide](docs/contributing.md) for details.

## License

MIT License - See [LICENSE](LICENSE) file for details

Agent Context Development 
# Agent Context – AI-Powered Personal Finance Analyzer (PFA)
*Version 0.3 – April 27 2025*

---
## 0  Mission
Deliver real‑time, fully‑classified financial insights with LLM‑driven analytics and minimal manual upkeep for Zach (and future users).

---
## 1  Current Snapshot
### 1.1  Project structure
```
.
├── data/{raw,interim,processed,reports}
├── src/{ingest.py,categorize.py,llm.py,report.py,main_report.py,cli.py,cache.py,...}
├── tests/
├── notebooks/
├── config.yml, .env, requirements.txt
└── .github/workflows/test.yml
```
### 1.2  Pipeline
```
raw → ingest → interim CSV → categorize (rules→fuzzy→LLM) → processed → reports/plots
```
### 1.3  LLM stack
- **Model:** gpt‑4o‑mini (T=0, 8 output tokens)
- **Wrapper:** `src/llm.py` with cache + back‑off
- **Keys:** project‑scoped `sk-proj-...`

### 1.4  Clean state
- ✅ Zero uncategorised rows across five accounts (Jan–Apr 2025)
- ✅ Vendor cache populated; CI passes

---
## 2  Low‑hanging LLM bolt‑ons (next sprint)
| ID | Feature | Effort | Status |
|----|---------|--------|--------|
| B‑1 | Executive narrative summary | 0.5 h | todo |
| B‑2 | Natural‑language query CLI (`pfa ask ...`) | 1 h | todo |
| B‑3 | Recurring‑payment detector | 45 m | todo |
| B‑4 | Anomaly explainer | 0.5 h | todo |
| B‑5 | Auto‑budget proposal | 15 m | todo |
| B‑6 | Goal‑progress blurb | 30 m | todo |
| B‑7 | Vendor clustering via LLM | 30 m | todo |
| B‑8 | Markdown→PDF compiler | 30 m | todo |

---
## 3  Expanded project inventory  
*(copied from latest snapshot)*

### 3.1  Data directories
```
data/
├── raw/                # original statements
├── interim/            # *_processed.csv per source file
├── processed/account_*/transactions.csv
├── reports/{large_transactions.csv, top_merchants.csv}
└── vendor_cache.json
```
### 3.2  Key source files & sizes
| File | Lines | Purpose |
|------|-------|---------|
| ingest.py | 136 | CSV/PDF normalisation |
| categorize.py | 193 | Rules→fuzzy→LLM categoriser |
| llm.py |  85 | GPT‑4o‑mini wrapper with cache |
| report.py | 361 | Analytics + plots |
| main_report.py | 201 | CLI entry for consolidated report |
| cache.py |  24 | JSON vendor cache |

### 3.3  Current capabilities
- Multi‑account ETL, vendor normalisation, zero‑uncategorised guarantee
- Monthly & category summaries, top merchants, large‑txn flags, PNG charts

### 3.4  Technical debt / TODO
1. PDF OCR fallback  
2. Batch LLM classify (implemented) → integrate into CLI flag  
3. Streamlit dashboard MVP  
4. Banking API ingestion  
5. Vendor alias CSV optional over LLMinfer

---
## 4  Acceptance tests
1. `pytest` green  
2. `pfa cli --refresh --dry-run` returns zero uncategorised  
3. `pfa report --with-summary` writes `summary.md` & `report.pdf`

---
*End v0.3 context*

