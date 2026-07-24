.PHONY: clean docs lint test coverage release sdist

help:
	@echo "clean - remove build and Python artifacts"
	@echo "docs - build the documentation"
	@echo "lint - run ruff"
	@echo "test - run tests"
	@echo "coverage - check code coverage"
	@echo "release - package and upload a release"
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
	ruff check tinycontent tests demo
	ruff format --check tinycontent tests demo

test:
	pytest

coverage:
	pytest --cov=tinycontent --cov-report=term-missing

release: clean lint test sdist
	twine upload -r pypi dist/*

sdist: clean
	python -m build
	ls -l dist

docs:
	cd docs && sphinx-build -W -b html . _build/html
