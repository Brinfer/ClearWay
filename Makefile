#
# Makefile of the project
#

# Raspberry adress :
RASPBERRY_ADDRESS = clearwayPi

# Login/password of the Raspberry :
RASPBERRY_LOGIN = pi
RASPBERRY_PASSWORD = clearwayPi

# Terminal to use for the ssh connexion (sshpass and ssh required)
TERM = gnome-terminal # gnome-terminal # xterm
TERMOPTIONS = -- # -- (for gnome-terminal) # -e (for xterm)


export PROG = clearway

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
	rm -rf report/
	find ./clearway -type d -name __pycache__ -exec rm -rf {} \;
	find ./explo -type d -name __pycache__ -exec rm -rf {} \;
	find ./tests -type d -name __pycache__ -exec rm -rf {} \;

build:
	python -m build

upload:
ifeq ($(TARGET), raspberry)
	sshpass -p '$(RASPBERRY_PASSWORD)' scp -r $(PROG) $(RASPBERRY_LOGIN)@$(RASPBERRY_ADDRESS):$(PROG)
endif

# Open a terminal on the Raspberry.
term:
ifeq ($(TARGET), raspberry)
	$(TERM) $(TERMOPTIONS) sshpass -p '$(RASPBERRY_PASSWORD)' ssh -t $(RASPBERRY_LOGIN)@$(RASPBERRY_ADDRESS)
endif
