# Project Context

## Purpose
Build a cryptocurrency backtester to fetch historical data, simulate trading strategies, and visualize performance (ROI, Drawdown).

## Tech Stack
- Python 3.x
- pandas (Data manipulation)
- ccxt (Crypto data fetching)
- matplotlib (Visualization)

## Project Conventions

### Code Style
- PEP 8
- Type hinting for all function signatures.
- Docstrings for all classes and methods.

### Architecture Patterns
- Modular design: `DataLoader`, `Strategy`, `Backtester`, `Visualization`.
- Strategy Pattern for different trading strategies.

## External Dependencies
- CCXT (Exchange APIs)
