.PHONY: help install run test clean migrate worker

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run the Flask application"
	@echo "  make worker     - Run Celery worker"
	@echo "  make test       - Run tests"
	@echo "  make migrate    - Run database migrations"
	@echo "  make clean      - Clean up temporary files"

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

run:
	python run.py

worker:
	celery -A celery_worker.celery worker --loglevel=info

test:
	pytest --cov=. --cov-report=html

migrate:
	flask db upgrade

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
