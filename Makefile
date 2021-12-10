#
# Makefile of the project
#

# Raspberry adress :
RASPBERRY_ADDRESS = clearwayPi

# Login/password of the Raspberry :
RASPBERRY_LOGIN = pi

# Terminal to use for the ssh connexion (sshpass and ssh required)
TERM = gnome-terminal # gnome-terminal # xterm
TERMOPTIONS = -- # -- (for gnome-terminal) # -e (for xterm)

PROG_FOLDER = clearway
PROG_PACKAGE = clearway*.tar.gz
PROG_PACKAGE_FOLDER = dist/$(PROG_PACKAGE)

#
# Makefile rules.
#

# Compilation.
all:

# Cleaning-up.
.PHONY: clean

clean:
	rm -f *.log
	rm -rf dist/
	rm -rf clearway.egg-info/
	rm -rf reports/
	rm -rf .coverage
	find ./clearway -type d -name __pycache__ -exec rm -rf {} \;
	find ./explo -type d -name __pycache__ -exec rm -rf {} \;
	find ./tests -type d -name __pycache__ -exec rm -rf {} \;
	cd documents/research && rm -rf _minted* && latexmk -C && cd ../..

build:
	python3 -m build

upload:
	scp -r $(PROG_PACKAGE_FOLDER) $(RASPBERRY_LOGIN)@$(RASPBERRY_ADDRESS):/home/$(RASPBERRY_LOGIN)/PROG_FOLDER

upload_package: build
	scp -r $(PROG_PACKAGE_FOLDER) $(RASPBERRY_LOGIN)@$(RASPBERRY_ADDRESS):/home/$(RASPBERRY_LOGIN)

install: upload_package
	ssh -t $(RASPBERRY_LOGIN)@$(RASPBERRY_ADDRESS) 'pip uninstall -y clearway && pip install -U $(PROG_PACKAGE) && rm $(PROG_PACKAGE)'

launch:
	python3 -m clearway --no-gpio -i ../test/OpenCV/Tests_IA/bicycle_1fps.mp4 --yolo-weights ./resources/yolov2-tiny.weights --yolo-cfg ./resources/yolov2-tiny.cfg

check:
	python -m flake8 --config setup.cfg
	python -m black --check --config pyproject.toml clearway/
	python -m mypy --config-file setup.cfg clearway/

# Open a terminal on the Raspberry.
term:
	ssh -t $(RASPBERRY_LOGIN)@$(RASPBERRY_ADDRESS)
