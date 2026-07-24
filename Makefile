.PHONY: clean docs lint test coverage sdist

# All tests/python/dependency commands run inside the dev container, not
# on the host - see the hard rule in CLAUDE.md.
RUN = docker compose run --rm web

help:
	@echo "clean - remove build and Python artifacts"
	@echo "docs - build the documentation"
	@echo "lint - run ruff"
	@echo "test - run tests"
	@echo "coverage - check code coverage"
	@echo "sdist - package"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf *.egg/
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	rm -f coverage.xml
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .ruff_cache

lint:
	$(RUN) ruff check tinycontent tests demo
	$(RUN) ruff format --check tinycontent tests demo

test:
	$(RUN) pytest

coverage:
	$(RUN) pytest --cov=tinycontent --cov-report=term-missing

# No PyPI publishing is set up for this fork yet (twine is still declared
# in pyproject.toml's "dev" extra for whenever that changes). Uncomment and
# add "release" back to .PHONY/help above once a release process exists.
# release: clean lint test sdist
# 	$(RUN) twine upload -r pypi dist/*

sdist: clean
	$(RUN) python -m build
	ls -l dist

docs:
	$(RUN) sh -c "cd docs && sphinx-build -W -b html . _build/html"
