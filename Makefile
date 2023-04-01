.DEFAULT_GOAL := all
sources = fsmparser tests

.PHONY: setup
setup:
	pip install pipx
	pipx install hatch
	pipx install black
	pipx install ruff

.PHONY: install
install:
	python -m pip install -U pip
	pip install -r requirements/all.txt
	pip install -e .

.PHONY: refresh-lockfiles
refresh-requirements:       ## Sync lockfiles with requirements files.
	bash requirements/refresh.sh

.PHONY: rebuild-lockfiles
rebuild-lockfiles:       ## Rebuild lockfiles from scratch, updating all dependencies
	bash requirements/rebuild.s

.PHONY: format
format:
	black $(sources)
	ruff --fix $(sources)

.PHONY: lint
lint:
	ruff $(sources)
	black $(sources) --check --diff

.PHONY: typecheck
mypy:
	mypy $(sources)

.PHONY: test
test:
	coverage run -m pytest --durations=10

.PHONY: testcov
testcov: test
	@echo "building coverage html"
	@coverage html

.PHONY: testcov-compile
testcov-compile: build-trace test
	@echo "building coverage html"
	@coverage html

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]'`
	rm -f `find . -type f -name '*~'`
	rm -f `find . -type f -name '.*~'`
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	rm -rf site
	rm -rf coverage.xml
