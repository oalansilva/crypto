# Crypto Backtester

A full-stack web application for backtesting cryptocurrency trading strategies with real-time visualization and performance metrics.

## Features

- 🚀 **Quick Start Presets**: Pre-configured backtest scenarios for instant testing
- 📊 **Real-time Visualization**: Interactive equity curves and performance charts
- 📈 **Multiple Strategies**: Compare up to 3 strategies simultaneously
- 🎯 **Comprehensive Metrics**: Sharpe ratio, max drawdown, win rate, and more
- 💾 **History Tracking**: View and manage all your backtest runs
- ⚡ **Async Execution**: Non-blocking background processing for long-running backtests

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Required for runtime databases
- **AsyncIO**: Asynchronous background workers

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **TailwindCSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **Recharts**: Charting library
- **React Router**: Client-side routing

## Project Structure

```
crypto/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app entry
│   │   ├── api.py          # API endpoints
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── models.py       # Database models
│   │   ├── services/       # Business logic
│   │   └── workers/        # Background jobs
│   ├── requirements.txt
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── lib/           # API client
│   │   ├── pages/         # Page components
│   │   ├── App.tsx        # Main app
│   │   └── main.tsx       # Entry point
│   └── package.json
│
└── [existing backtester modules]
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Create virtual environment** (if not already created):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure PostgreSQL envs**:
   ```bash
   cp backend/.env.example backend/.env
   ```

4. **Initialize database**:
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Start backend server**:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8003 --reload
   ```

   Backend will be available at: http://localhost:8003
   API docs: http://localhost:8003/docs

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

   Frontend will be available at: http://localhost:5173

### Docker Setup

For an isolated local stack with PostgreSQL, backend, frontend, and background worker:

```bash
cp .env.docker.example .env.docker.local
make docker-up
```

Services:
- Frontend: http://localhost:5173
- Backend: http://localhost:8003
- Backend docs: http://localhost:8003/docs
- PostgreSQL: `localhost:5432`

Notes:
- `docker-compose.yml` is configured for development with bind mounts and hot reload.
- The backend container runs `alembic upgrade head` before starting FastAPI.
- The worker container runs the current background routines (`signal_monitor` and signal feed snapshot refresh).
- A lightweight `postgres-backup` service writes daily logical dumps into `./backups/postgres`.
- Multi-stage Dockerfiles are available for backend, frontend, and worker images.
- The `Makefile` uses `.env.docker.local` to avoid conflicting with the repo's existing `.env`.
- If ports `5432`, `8003`, or `5173` are already in use, override `POSTGRES_PORT`, `BACKEND_PORT`, and `FRONTEND_PORT` in `.env.docker.local`.

Useful commands:

```bash
make db-migrate
make db-backup
```

### Start/Stop Scripts (Ubuntu)

From the repo root:
```bash
./stop.sh
./start.sh
```

O projeto `crypto` é independente e sobe apenas o runtime dele.

`stop.sh` stops those systemd services when available and falls back to stopping `uvicorn`/`vite` processes.

`start.ps1` and `stop.ps1` are kept only for legacy Windows workflows and are deprecated.

## Usage

### Running Presets

1. Navigate to the **Playground** tab
2. Choose from 3 pre-configured presets:
   - **BTC Swing (2 years, 4h)**: Compare 3 strategies with stop/take
   - **ETH Swing (2 years, 1d)**: Daily timeframe comparison
   - **BTC Trend (1 year, 1d)**: Single SMA Cross strategy
3. Click "Run Backtest" to start execution
4. Monitor progress in the **History** tab
5. View results when status changes to "DONE"

### Viewing Results

1. Go to **History** tab
2. Find completed backtests (green "DONE" status)
3. Click "View Results" to see:
   - Equity curve comparison chart
   - Performance metrics for each strategy
   - Total return, max drawdown, Sharpe ratio
   - Win rate and trade statistics

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/presets` | GET | List preset configurations |
| `/api/backtest/run` | POST | Start single strategy backtest |
| `/api/backtest/compare` | POST | Start multi-strategy comparison |
| `/api/backtest/status/{run_id}` | GET | Get backtest status |
| `/api/backtest/result/{run_id}` | GET | Get backtest results |
| `/api/backtest/runs` | GET | List backtest history |
| `/api/backtest/runs/{run_id}` | DELETE | Delete backtest run |

## Development

### Backend Development

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### CI / E2E

```bash
npm --prefix frontend run test:playground-label
./backend/.venv/bin/python -m pytest -q backend/tests
npm --prefix frontend run test:e2e
```

### Lint / Format

```bash
./backend/.venv/bin/python -m black backend
npm --prefix frontend run lint
```

### Coverage Gate

```bash
./backend/.venv/bin/python -m pytest -q backend/tests \
  --cov=backend/app \
  --cov-config=.coveragerc \
  --cov-fail-under=70 \
  --cov-report=term \
  --cov-report=xml:coverage.xml
```

PRs now enforce two backend coverage gates:

- `>= 70%` total backend line coverage for the repository baseline.
- `>= 70%` differential coverage on changed lines under `backend/app/**`.

The baseline now starts at `70%` while legacy/backtest-heavy modules remain excluded in `.coveragerc`.

Contribution guide:
`CONTRIBUTING.md`

Branch protection checklist:
`docs/branch-protection.md`

Staging deploy setup:
`docs/staging-deploy.md`

### Building for Production

```bash
cd frontend
npm run build
```

## Configuration

### Backend (.env)

```env
DATABASE_URL=postgresql+psycopg2://crypto_app:password@127.0.0.1:5432/crypto_app
WORKFLOW_DB_ENABLED=1
WORKFLOW_DATABASE_URL=postgresql+psycopg2://workflow_registry:password@127.0.0.1:5432/workflow_registry
CRYPTO_DATABASE_URL=postgresql+psycopg2://crypto_app:password@127.0.0.1:5432/crypto_app
CRYPTO_WORKFLOW_DATABASE_URL=postgresql+psycopg2://workflow_crypto:password@127.0.0.1:5432/workflow_crypto
```

### Legacy Migration

```bash
./backend/.venv/bin/python backend/scripts/migrate_projects_to_postgres.py
```

## Projeto Kanban

O Kanban agora fica em [kanban/](/root/.openclaw/workspace/kanban) como projeto separado, com `backend/`, `frontend/`, `start.sh` e `stop.sh` próprios.

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8003/api
```

## Troubleshooting

### Backend Issues

**Port already in use**:
```bash
# Use a different port
python -m uvicorn app.main:app --port 8004
```

**Database config missing**:
```bash
# Configure PostgreSQL URLs in backend/.env before starting the stack
```

### Frontend Issues

**Module not found**:
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**CORS errors**:
- Ensure backend is running on port 8003
- Check `VITE_API_URL` in frontend/.env

## Future Enhancements

- [ ] Custom backtest form with parameter inputs
- [ ] Trade-by-trade analysis table
- [ ] Candlestick chart with trade markers
- [ ] Portfolio optimization
- [ ] Walk-forward analysis
- [ ] Export results to PDF/CSV
- [ ] User authentication
- [ ] Cloud deployment (Supabase/Vercel)

## License

MIT

## Author

Alan Silva
