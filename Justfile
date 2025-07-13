# list of commands
help:
    @just -l

sync:
    @echo "Syncing dependencies..."
    @uv sync --all-groups --all-extras

# Format code with ruff and isort
format:
    @echo "Formatting code with ruff..."
    @ruff format yaicli
    @ruff check --fix yaicli
    @ruff format tests
    @ruff check --fix tests
    @echo "Formatting code with isort..."
    @isort yaicli yaicli
    @isort yaicli tests

# Clean build artifacts
clean:
    @echo "Cleaning build artifacts..."
    @rm -rf build/ dist/ *.egg-info/
    @echo "Cleaning cache files..."
    @find . -type d -name "__pycache__" -exec rm -rf {} +
    @echo "Cleaning test artifacts..."
    @rm -rf .pytest_cache/
    @echo "Cleaning pdm build artifacts..."
    @rm -rf .pdm_build/ .pdm-build/
    @echo "Cleaning ruff cache..."
    @rm -rf .ruff_cache/

# Run tests with pytest
test:
    @echo "Running tests..."
    @pytest

# Build package with hatch (runs clean first)
build:
    @echo "Building package..."
    @rm -rf dist/
    @uv build