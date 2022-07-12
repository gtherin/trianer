.ONESHELL:

# Need to specify bash in order for conda activate to work.
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda

# Get versions
include config.mk
PYTHON_VERSION = $(shell echo ${ENV_NAME} | tail -c 5)
PACKAGE_NAME = $(shell basename ${PWD})

# Load package config info

create:
	$(CONDA) create -n ${ENV_NAME} python=$(PYTHON_VERSION) -y;

requirements:
	($(CONDA) activate ${ENV_NAME}; pip install -r requirements.txt;)

kernel:
	$(CONDA) activate ${ENV_NAME};
	ipython kernel install --user --name=${ENV_NAME};

install: create requirements kernel
	($(CONDA) activate ${ENV_NAME} ; python setup.py develop)

clean: clean-pyc
	@echo clean ${ENV_NAME};
	$(CONDA) activate base;
	$(CONDA) remove env -n ${ENV_NAME};
	rm -rf ~/.local/share/jupyter/kernels/${ENV_NAME};

env: create requirements kernel install

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +;
	find . -name '*.pyo' -exec rm --force {} +;

test: clean-pyc
	py.test --verbose --color=yes tests;
