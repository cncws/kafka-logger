.PHONY: clean test build release

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

clean:
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	rm -rf dist/ build/
	@echo "$(GREEN)Clean complete!$(NC)"

test:
	@echo "$(GREEN)Running tests...$(NC)"
	uv run pytest

build:
	@echo "$(GREEN)Building package...$(NC)"
	uv build

release: clean test build
	@echo "$(GREEN)Releasing package...$(NC)"
	uv publish --index em
