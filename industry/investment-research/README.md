# Investment Research Engine

A production-grade Python module for managing equity research notes, price target updates, opportunity screening, and portfolio alpha calculation.

## Features
- Create research notes with analyst thesis, target price, and rating (buy/hold/sell)
- Update price targets with rationale and history tracking
- Screen opportunities by rating, price, ticker, or analyst
- Calculate portfolio alpha vs market return
- Generate structured research reports with recommendations

## Usage
```python
from src.engine import InvestmentResearchEngine

engine = InvestmentResearchEngine()
note = engine.create_research_note("analyst-1", "AAPL", "Strong iPhone cycle", 200.0, "buy", current_price=150.0)
report = engine.generate_research_report(note.id)
buys = engine.screen_opportunities({"rating": "buy", "min_target_price": 150.0})
```
