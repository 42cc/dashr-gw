########################
# CONSTANTS
########################

SHELL=/bin/bash

PROJECT_NAME=gateway
BIND_TO=0.0.0.0
RUNSERVER_PORT=8000
SETTINGS=gateway.settings
TEST_APP=apps.core
APPS=apps
flake8=flake8 --max-complexity=6 --exclude '*migrations*'

PYTHONPATH=$(CURDIR)
MANAGE = PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(SETTINGS) django-admin.py


-include Makefile.def

########################
# END OF CONSTANTS
########################

########################
# TARGETS
########################

run:
	@echo Starting $(PROJECT_NAME)...
	$(MANAGE) runserver $(BIND_TO):$(RUNSERVER_PORT)

shell:
	@echo Starting shell...
	$(MANAGE) shell

flake8:
	$(flake8) gateway

test: flake8
	TESTING=1 PYTHONWARNINGS=ignore $(MANAGE) test $(TEST_OPTIONS) $(TEST_APP)

pre-install:
	-sudo apt-get install yui-compressor
	sudo npm install -g less

install:
	npm install
	pip install -r requirements.txt

post-install: webpack
	$(MAKE) migrate

webpack:
	webpack --config webpack.config.js

webpack-watch:
	webpack --config webpack.config.js --watch

collectstatic:
	@echo Collecting static
	$(MANAGE) collectstatic --noinput
	@echo Done

clean:
	@echo Cleaning up...
	find . | grep '\.pyc$' | xargs -I {} rm {}
	@echo Done

manage:
ifndef CMD
	@echo Please, spceify -e CMD=command argument to execute
else
	$(MANAGE) $(CMD)
endif

only_migrate:
ifndef APP_NAME
	@echo Please, specify -e APP_NAME=appname argument
else
	@echo Starting of migration of $(APP_NAME)
	$(MANAGE) migrate $(APP_NAME)
	@echo Done
endif

migrate:
ifndef APP_NAME
	@echo "You can also specify -e APP_NAME='app' to check if new migrations needed for some app"
	$(MANAGE) migrate
else
	@echo Starting of migration of $(APP_NAME)
	$(MANAGE) schemamigration $(APP_NAME) --auto
	$(MANAGE) migrate $(APP_NAME)
	@echo Done
endif

init_migrate:
ifndef APP_NAME
	@echo Please, specify -e APP_NAME=appname argument
else
	@echo Starting init migration of $(APP_NAME)
	$(MANAGE) schemamigration $(APP_NAME) --initial
	$(MANAGE) migrate $(APP_NAME)
	@echo Done
endif

########################
# END TARGETS
########################