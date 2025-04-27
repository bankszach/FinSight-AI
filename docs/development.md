# Development Guide

## Project Evolution

Originally a traditional financial statement analyzer, the project has evolved into an LLM-first personal finance tool. This document outlines the development process, architecture, and best practices.

## Architecture

### Data Processing Pipeline
```
Raw Statements → Normalization → AI Categorization → Analysis → Insights
   (CSV/PDF)      (ingest.py)     (categorize.py)   (report.py)  (LLM)
```

### Component Overview

1. **Data Ingestion** (`ingest.py`)
   - CSV/PDF processing
   - Data normalization
   - Format standardization

2. **Transaction Processing** (`categorize.py`)
   - Multi-stage categorization
   - Pattern matching
   - Data validation

3. **AI Integration** (`llm.py`)
   - LLM API interaction
   - Prompt management
   - Response processing

4. **Analysis Engine** (`report.py`)
   - Financial analysis
   - Visualization
   - Report generation

## Development Workflow

### 1. Setup
```bash
# Clone repository
git clone [repository-url]

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Development Process
1. Create feature branch
2. Implement changes
3. Run tests
4. Submit pull request

### 3. Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ingest.py
```

## Code Organization

### Source Structure
```
src/
├── __init__.py              # Package initialization
├── ingest.py                # Data ingestion
├── categorize.py            # Transaction categorization
├── llm.py                   # LLM integration
├── report.py                # Report generation
├── main_report.py           # Main analysis
├── cli.py                   # Command interface
├── cache.py                 # Caching utilities
├── consolidate.py           # Data consolidation
└── analyze_large_transactions.py  # Transaction analysis
```

### Data Structure
```
data/
├── raw/                     # Original statements
├── interim/                 # Processed data
├── processed/               # Analysis outputs
└── reports/                 # Generated reports
```

## Best Practices

### 1. Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document functions and classes
- Write unit tests

### 2. AI Integration
- Cache LLM responses
- Implement rate limiting
- Handle API errors gracefully
- Validate responses

### 3. Data Processing
- Validate input data
- Handle edge cases
- Implement logging
- Use appropriate data types

## Development Roadmap

### Phase 1: Core Enhancement
- [ ] Enhanced transaction categorization
- [ ] Natural language query interface
- [ ] Automated insight generation

### Phase 2: Advanced Features
- [ ] Predictive analytics
- [ ] Budget optimization
- [ ] Investment analysis

### Phase 3: Integration
- [ ] Banking API integration
- [ ] Mobile interface
- [ ] Real-time updates

## Troubleshooting

### Common Issues
1. **API Rate Limiting**
   - Implement caching
   - Use exponential backoff
   - Monitor usage

2. **Data Processing Errors**
   - Validate input formats
   - Handle missing data
   - Log errors

3. **Performance Issues**
   - Profile code
   - Optimize database queries
   - Implement caching

## Contributing

See [Contributing Guide](contributing.md) for detailed contribution guidelines. 