.PHONY: help format lint test pre-commit verify clean

help:
	@echo "🚀 vnstock_dev Development Workflow Commands:"
	@echo "----------------------------------------------------------------"
	@echo "make verify      : 🌟 Run everything: format, lint, pre-commit, and test."
	@echo "make format      : 🎨 Auto-format and auto-fix code using Ruff."
	@echo "make lint        : 🔍 Check code style and errors using Ruff."
	@echo "make test        : 🧪 Run all Pytest suites (Core & Unified UI)."
	@echo "make pre-commit  : 🛡️ Run pre-commit hooks on all files."
	@echo "make clean       : 🧹 Clean up cache and compiled files."
	@echo "----------------------------------------------------------------"

format:
	@echo "\n🎨 Formatting and Auto-fixing code with Ruff..."
	ruff check --fix .
	ruff format .

lint:
	@echo "\n🔍 Running Linter..."
	ruff check .

test:
	@echo "\n🧪 Running Test Suites..."
	@echo "1. Unified UI Tests..."
	PYTHONPATH=. pytest tests/unified_ui/
	@echo "2. Core & Explorer Tests..."
	PYTHONPATH=. pytest tests/

pre-commit:
	@echo "\n🛡️ Running Pre-commit Hooks..."
	pre-commit run --all-files

verify: format lint pre-commit test
	@echo "\n✅ Vượt qua toàn bộ bài kiểm tra! Mã nguồn của bạn đã sạch, an toàn và sẵn sàng để Commit / Release."

clean:
	@echo "\n🧹 Cleaning up caches..."
	rm -rf .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Done!"
