.ONESHELL:

# Need to specify bash in order for conda activate to work.
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda

# Get versions
include config.mk
PYTHON_VERSION = $(shell echo ${ENV_NAME} | tail -c 5)
PACKAGE_NAME = $(shell basename ${PWD})
ONLINE_CONNECT = $(shell cat ~/.ssh/onl)
LOCAL_DEPENDENCIES = $(shell grep LOCAL_DEPENDENCIES config.mk | cut -c 20-)


nstopv:
	$(CONDA) activate ${ENV_NAME}; cd ../nstopv && pip install develop -e .;

dapir:
	$(CONDA) activate ${ENV_NAME}; cd ../dapir && pip install develop -e .;

create:
	$(CONDA) create -n ${ENV_NAME} python=$(PYTHON_VERSION) -y;

requirements:
	($(CONDA) activate ${ENV_NAME}; pip install -r requirements.txt;)


kernel:
	$(CONDA) activate ${ENV_NAME}; pip install ipython ipykernel; ipython3 kernel install --user --name=${ENV_NAME};

install: $(LOCAL_DEPENDENCIES)
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

package:
	# Build package
	python setup.py bdist_wheel -d /mnt/tutar/git/dist/
	#python setup.py sdist -d /mnt/google_drive/packages/
	# Dump last version number in specific file
	python setup.py --version > /mnt/tutar/git/dist/${PACKAGE_NAME}.lastversion
	# Copy the colab installer to google drive
	cp -f /home/guydegnol/projects/colab_installer.py /mnt/tutar/git/dist/packages/

notebook:
	mkdir -p /home/guydegnol/export/projects/${PACKAGE_NAME}
	# Copy the notebooks to google drive
	#rsync -avu --progress --delete /home/guydegnol/projects/${PACKAGE_NAME}/notebooks/*.ipynb /home/guydegnol/export/projects/${PACKAGE_NAME}
	#cp /home/guydegnol/projects/${PACKAGE_NAME}/README.rst /home/guydegnol/export/projects/${PACKAGE_NAME}/

export-config:
	/usr/bin/google-drive-ocamlfuse /home/guydegnol/export/

web:
	# Sync website
	#lftp -u webmaster@guydegnol.net,${DIST_PARAM} privftp.online.net -e "mirror -e -R /home/guydegnol/projects/web/guydegnol.net www ; quit"
	@lftp -u ${ONLINE_CONNECT} privftp.online.net -e "mirror -e -R /home/guydegnol/projects/web/guydegnol.net www ; quit"
    #curlftpfs privftp.online.net /mnt/online -o user=${ONLINE_CONNECT},allow_other -o uid=1000 -o gid=1000


sdist: package notebooks web
