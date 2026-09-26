.DEFAULT_GOAL := help
SHELL := $(shell which bash)
PYTHON_VERSION := 3.13.7

.PHONY: help build serve deploy publish clean check sync-calendar \
	black black-check pylint mypy shellcheck \
	unit unit-update-golden integration static static-check \
	clean-cache clean-venv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

sync-calendar: ## Regenerate static/events.ics from data/events.json
	python3 scripts/sync_calendar.py

build: sync-calendar ## Build the Hugo site
	hugo --minify

serve: sync-calendar ## Run local development server
	hugo server -D

deploy: check build ## Deploy site to S3 bucket
	./scripts/deploy.sh

publish: sync-calendar check build deploy ## Sync calendar data, verify, build, and deploy -- one-shot
	@echo "✓ Published"

clean: ## Remove generated files
	rm -rf public resources static/events.ics

check: sync-calendar ## Run common checks
	@echo "Running checks..."
	@command -v hugo >/dev/null 2>&1 || { echo "Error: hugo not found"; exit 1; }
	@command -v aws >/dev/null 2>&1 || { echo "Error: aws cli not found"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "Error: python3 not found"; exit 1; }
	@echo "✓ Hugo, AWS CLI, and Python 3 available"
	@hugo --quiet || { echo "Error: Hugo build failed"; exit 1; }
	@echo "✓ Hugo build successful"

.venv: requirements.txt ## create venv if it doesn't exist
	python3 -m venv .venv
	source .venv/bin/activate && pip install --upgrade pip setuptools
	source .venv/bin/activate && pip install -r requirements.txt
	touch .venv

clean-venv: clean-cache ## re-create virtual env
	rm -rf .venv
	$(MAKE) .venv

black: .venv ## format python files
	source .venv/bin/activate && git ls-files '*.py' | xargs black --line-length=79

black-check: .venv ## check python formatting without modifying
	source .venv/bin/activate && git ls-files '*.py' | xargs black --check --line-length=79

pylint: .venv ## lint python files
	source .venv/bin/activate && git ls-files '*.py' | xargs pylint --max-line-length=90

mypy: .venv ## type check python files
	source .venv/bin/activate && python3 -m mypy $(shell git ls-files '*.py')

shellcheck: ## check shell scripts
	git ls-files 'scripts/*.sh' | xargs --no-run-if-empty shellcheck --severity=error --format=gcc

unit: .venv ## run unit tests
	source .venv/bin/activate && python3 -m pytest -v -m "unit" tests/

unit-update-golden: .venv ## update golden files
	source .venv/bin/activate && python3 -m pytest -v -m "unit" tests/ --update_golden

integration: .venv ## run integration tests (requires credentials)
	source .venv/bin/activate && python3 -m pytest -v -m "integration" tests/

static-check: black-check mypy shellcheck pylint unit ## run all static checks (CI)

static: black mypy shellcheck pylint unit ## run all static checks with auto-format

clean-cache: ## clean python and pytest cache data
	@find . -type f -name "*.py[co]" -delete -not -path "./.venv/*"
	@find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache
