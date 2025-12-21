# Route Optimizer - Project Structure

```
hackathon/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── LICENSE                # MIT License
├── README.md              # Project documentation
├── demo.py               # One-command demo script
│
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # System architecture
│   ├── DATA_MODELS.md     # API schemas
│   ├── REQUIREMENTS.md    # Detailed requirements
│   └── DEMO.md           # Demo instructions
│
├── models/                # Data models
│   ├── __init__.py
│   └── schemas.py         # Pydantic models
│
├── utils/                 # Core utilities
│   ├── __init__.py
│   ├── algorithm.py       # Genetic Algorithm
│   ├── distance.py        # Distance calculation
│   ├── cities.py          # City database
│   ├── ai_summary.py      # Gemini LLM integration
│   └── recalculation.py   # Real-time updates
│
├── static/                # Frontend
│   ├── index.html         # Main UI
│   ├── app.js            # JavaScript logic
│   ├── styles.css        # Main styles
│   └── realtime.css      # Real-time UI styles
│
└── scripts/               # Testing & benchmarks
    ├── benchmark.py       # Performance tests
    ├── test_*.py          # Various tests
    └── quick_test.py      # Quick validation
```

## Key Files

- **main.py**: FastAPI REST API with 6 endpoints
- **utils/algorithm.py**: Genetic Algorithm implementation (593 lines)
- **static/app.js**: Frontend logic (860 lines)
- **docs/**: Comprehensive documentation with Mermaid diagrams

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run demo (one command!)
python demo.py

# Or start manually
python main.py
```
