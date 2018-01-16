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

worker:
	celery -B -A gateway worker -l INFO

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
	mkdir fieldkeys
	sudo apt-get install python-keyczar
	keyczart create --location=fieldkeys --purpose=crypt
	keyczart addkey --location=fieldkeys --status=primary --size=256

install:
	npm install
	pip install -r requirements.txt

post-install:
	webpack -p
	$(MAKE) migrate
	$(MANAGE) loaddata initial_pages.json

webpack:
	webpack --config webpack.config.js

webpack-watch:
	webpack --config webpack.config.js --watch

collectstatic:
	@echo Collecting static
	$(MANAGE) collectstatic --noinput -i components -i less
	@echo Done

clean:
	@echo Cleaning up...
	find . -name '*.pyc' -delete
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