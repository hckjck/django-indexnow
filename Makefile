.DEFAULT_GOAL := help

.PHONY: help test clean build check package bump-version tag-version

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

bump-version: ## Bump version in pyproject.toml and indexnow/__init__.py (usage: make bump-version VERSION=0.1.1)
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make bump-version VERSION=x.y.z[-suffix]"; \
		exit 1; \
	fi
	@python3 scripts/bump_version.py "$(VERSION)"

tag-version: ## Create git tag from pyproject.toml version (use DRY_RUN=1 to preview)
	@python3 scripts/tag_version.py $(if $(DRY_RUN),--dry-run,)
