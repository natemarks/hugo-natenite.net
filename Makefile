.PHONY: help build serve deploy clean check

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the Hugo site
	hugo --minify

serve: ## Run local development server
	hugo server -D

deploy: check build ## Deploy site to S3 bucket
	./scripts/deploy.sh

clean: ## Remove generated files
	rm -rf public resources

check: ## Run common checks
	@echo "Running checks..."
	@command -v hugo >/dev/null 2>&1 || { echo "Error: hugo not found"; exit 1; }
	@command -v aws >/dev/null 2>&1 || { echo "Error: aws cli not found"; exit 1; }
	@echo "✓ Hugo and AWS CLI available"
	@hugo --quiet || { echo "Error: Hugo build failed"; exit 1; }
	@echo "✓ Hugo build successful"
