.PHONY: install install-dev lint format type-check test test-cov clean help setup-env check-env check-airtable find-base-id setup-complete

# Default target
help:
	@echo "Available commands:"
	@echo "  install           Install production dependencies"
	@echo "  install-dev       Install development dependencies"
	@echo "  install-pip       Install using pip (fallback)"
	@echo "  lint              Run linting with ruff"
	@echo "  format            Format code with ruff"
	@echo "  type-check        Run type checking with mypy"
	@echo "  test              Run tests with pytest"
	@echo "  test-cov          Run tests with coverage report"
	@echo "  clean             Clean up temporary files"
	@echo "  all               Run lint, type-check, and test"
	@echo "  check-airtable    Verify Airtable connection"
	@echo "  find-base-id      Find your Airtable Base ID"
	@echo "  setup-complete    Complete setup process"

# Install production dependencies with UV
install:
	@if command -v uv > /dev/null 2>&1; then \
		echo "Using UV to install dependencies..."; \
		uv sync; \
	else \
		echo "UV not found, using pip..."; \
		uv pip install -r requirements.txt; \
	fi

# Install development dependencies with UV
install-dev:
	@if command -v uv > /dev/null 2>&1; then \
		echo "Using UV to install dev dependencies..."; \
		uv sync --dev; \
	else \
		echo "UV not found, using pip..."; \
		uv pip install -r requirements.txt -r requirements-dev.txt; \
	fi


# Install using pip (fallback)
install-pip:
	uv pip install -r requirements.txt -r requirements-dev.txt

# Run linting
lint:
	@if command -v uv > /dev/null 2>&1; then \
		uv run ruff check .; \
	else \
		python -m ruff check .; \
	fi

# Format code
format:
	@if command -v uv > /dev/null 2>&1; then \
		uv run ruff format .; \
		uv run ruff check --fix .; \
	else \
		python -m ruff format .; \
		python -m ruff check --fix .; \
	fi

# Run type checking
type-check:
	@if command -v uv > /dev/null 2>&1; then \
		uv run mypy .; \
	else \
		python -m mypy .; \
	fi

# Run tests
test:
	@if command -v uv > /dev/null 2>&1; then \
		uv run pytest tests/ -v; \
	else \
		python -m pytest tests/ -v; \
	fi

# Run tests with coverage
test-cov:
	@if command -v uv > /dev/null 2>&1; then \
		uv run pytest tests/ --cov=./ --cov-report=html -v; \
	else \
		python -m pytest tests/ --cov=./ --cov-report=html -v; \
	fi

# Clean up temporary files
clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache htmlcov .uv .venv
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete

# Run all checks
all: lint type-check test

# Verify Airtable connection
check-airtable:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -m scripts.setup_airtable_base; \
	else \
		python -m scripts.setup_airtable_base; \
	fi

# Find Base ID
find-base-id:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -m scripts.find_base_id; \
	else \
		python -m scripts.find_base_id; \
	fi

# Check environment
check-env:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -c "from decouple import config; print('API Key:', config('AIRTABLE_API_KEY', default='NOT_SET')[:10] + '...')"; \
	else \
		python -c "from decouple import config; print('API Key:', config('AIRTABLE_API_KEY', default='NOT_SET')[:10] + '...')"; \
	fi

# Setup complete environment
create-forms:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -m scripts.create_airtable_forms; \
	else \
		python -m scripts.create_airtable_forms; \
	fi

# Setup complete environment including forms
setup-complete: install-dev check-airtable create-forms
	@echo "Environment setup complete!"
	@echo "Please follow the form creation instructions above"

# Script shortcuts
compress:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -m scripts.compress_json $(ARGS); \
	else \
		python -m scripts.compress_json $(ARGS); \
	fi

decompress:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -m scripts.decompress_json $(ARGS); \
	else \
		python -m scripts.decompress_json $(ARGS); \
	fi

shortlist:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -m scripts.shortlist_candidates $(ARGS); \
	else \
		python -m scripts.shortlist_candidates $(ARGS); \
	fi

evaluate:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -m scripts.llm_evaluation $(ARGS); \
	else \
		python -m scripts.llm_evaluation $(ARGS); \
	fi

# Helper for manual form creation
forms-help:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -m scripts.form_creation_helper; \
	else \
		python -m scripts.form_creation_helper; \
	fi

# Open Airtable base in browser
open-airtable:
	@if command -v uv > /dev/null 2>&1; then \
		uv run python -c "import webbrowser; from decouple import config; webbrowser.open(f'https://airtable.com/{config(\"AIRTABLE_BASE_ID\", default=\"\")}')"; \
	else \
		python -c "import webbrowser; from decouple import config; webbrowser.open(f'https://airtable.com/{config(\"AIRTABLE_BASE_ID\", default=\"\")}')"; \
	fi