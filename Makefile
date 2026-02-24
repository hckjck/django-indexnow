.PHONY: test

test:
	env/python/bin/python -m django test --settings=tests.test_settings
