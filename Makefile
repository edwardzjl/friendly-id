
# Default target executed when no arguments are given to make.
all: build

lint:
	black . --check

format:
	black .

test:
	python -m unittest

build:
	python -m build

######################
# HELP
######################

help:
	@echo '----'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo 'test                         - run unit tests'
