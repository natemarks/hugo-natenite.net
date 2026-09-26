.PHONY: help build serve deploy clean check sync-calendar

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
