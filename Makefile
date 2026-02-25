.DEFAULT_GOAL := help

.PHONY: help test clean build check package

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*## ' Makefile | sed 's/:.*## /\t/'

test: ## Run Django test suite
	env/python/bin/python -m django test --settings=tests.test_settings

clean: ## Remove build artifacts
	rm -rf build dist *.egg-info

build: clean ## Build sdist and wheel
	python3 setup.py sdist bdist_wheel

check: ## Validate built artifacts (twine if available)
	@if python3 -m twine --version >/dev/null 2>&1; then \
		python3 -m twine check dist/*; \
	else \
		ls -1 dist/* >/dev/null 2>&1; \
		echo "twine is not installed; skipped twine metadata check"; \
	fi

package: build check ## Build and validate package artifacts
