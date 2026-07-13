# Quick Start Guide

## Option 1: Docker (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# Start all services (PostgreSQL, Redis, Flask, Celery)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

The application will be available at `http://localhost:5000`

## Option 2: Local Development

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Redis 7+

### Setup

1. **Run setup script:**

   On Linux/Mac:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   On Windows:
   ```bash
   setup.bat
   ```

2. **Configure environment:**

   Edit `.env` file with your database and Redis credentials.

3. **Create database:**

   ```bash
   createdb resume_analyzer
   ```

4. **Initialize database:**

   ```bash
   # Activate virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Run migrations
   flask db upgrade
   ```

5. **Start services:**

   Open 3 terminal windows:

   **Terminal 1 - Redis:**
   ```bash
   redis-server
   ```

   **Terminal 2 - Celery Worker:**
   ```bash
   source .venv/bin/activate
   celery -A celery_worker.celery worker --loglevel=info
   ```

   **Terminal 3 - Flask App:**
   ```bash
   source .venv/bin/activate
   python run.py
   ```

6. **Verify installation:**

   Visit `http://localhost:5000/health` - you should see:
   ```json
   {
     "status": "healthy",
     "service": "resume-analyzer"
   }
   ```

## Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Common Commands

```bash
# Using Makefile
make install    # Install dependencies
make run        # Run Flask app
make worker     # Run Celery worker
make test       # Run tests
make migrate    # Run database migrations
make clean      # Clean temporary files

# Manual commands
python run.py                                      # Start Flask app
celery -A celery_worker.celery worker --loglevel=info  # Start Celery worker
pytest                                             # Run tests
flask db migrate -m "Description"                  # Create migration
flask db upgrade                                   # Apply migrations
```

## Troubleshooting

### Database connection error

Make sure PostgreSQL is running and the database exists:
```bash
createdb resume_analyzer
```

### Redis connection error

Make sure Redis is running:
```bash
redis-server
```

### Import errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Port already in use

Change the port in `.env`:
```
PORT=8000
```

## Next Steps

1. Review the [README.md](README.md) for detailed documentation
2. Check the [design document](.kiro/specs/resume-analyzer-redesign/design.md) for architecture details
3. Start implementing features according to the [task list](.kiro/specs/resume-analyzer-redesign/tasks.md)
