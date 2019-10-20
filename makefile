help:
	@echo
	@echo 'deployment:  build, publish, tag'
	@echo 'versioning:  bump-patch, bump-minor, bump-major'
	@echo 'setup:       setup-deps, setup-env'

# Testing helpers --------------------------------------------------------------

clean:
	$(info cleaning demo directory)
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__
	@rm -rvf build dist *.egg-info demo


# Deployment Helpers -----------------------------------------------------------

build: clean
	python3 setup.py sdist bdist_wheel --universal

publish:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

tag:
	git tag `vbump | egrep -o '[0-9].*'`


# Version Helpers --------------------------------------------------------------

bump-patch:
	vbump --patch
	make sync-version
	git reset --
	git add mnamer/__version__.py
	git add pyproject.toml
	git commit -m "Patch version bump"

bump-minor:
	vbump --minor
	make sync-version
	git reset --
	git add mnamer/__version__.py
	git add pyproject.toml
	git commit -m "Minor version bump"

bump-major:
	vbump --major
	make sync-version
	git reset --
	git add mnamer/__version__.py
	git add pyproject.toml
	git commit -m "Major version bump"


# Setup Helpers ----------------------------------------------------------------

setup-deps:
	pip3 install -r requirements-dev.txt

setup-env:
	deactivate || true
	rm -rf venv
	virtualenv venv
	./venv/bin/pip install -r requirements-dev.txt
