MANAGE=./manage.py
APP=footprints
FLAKE8=./ve/bin/flake8

jenkins: ./ve/bin/python validate test flake8 jshint

./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	chmod +x manage.py bootstrap.py
	./bootstrap.py

jshint: node_modules/jshint/bin/jshint
	./node_modules/jshint/bin/jshint media/js/app/ media/js/xeditable

node_modules/jshint/bin/jshint:
	npm install jshint --prefix .

test: ./ve/bin/python
	$(MANAGE) jenkins --pep8-exclude=migrations --enable-coverage --coverage-rcfile=.coveragerc

flake8: ./ve/bin/python
	$(FLAKE8) $(APP) --max-complexity=12

runserver: ./ve/bin/python validate
	$(MANAGE) runserver

migrate: ./ve/bin/python validate jenkins
	$(MANAGE) migrate

validate: ./ve/bin/python
	$(MANAGE) validate

shell: ./ve/bin/python
	$(MANAGE) shell_plus

clean:
	rm -rf ve
	rm -rf media/CACHE
	rm -rf reports
	rm celerybeat-schedule
	rm .coverage
	find . -name '*.pyc' -exec rm {} \;

pull:
	git pull
	make validate
	make test
	make migrate
	make flake8

rebase:
	git pull --rebase
	make validate
	make test
	make migrate
	make flake8

syncdb: ./ve/bin/python
	$(MANAGE) syncdb

collectstatic: ./ve/bin/python validate
	$(MANAGE) collectstatic --noinput --settings=$(APP).settings_production

# run this one the very first time you check
# this out on a new machine to set up dev
# database, etc. You probably *DON'T* want
# to run it after that, though.
install: ./ve/bin/python validate jenkins
	createdb $(APP)
	$(MANAGE) syncdb --noinput
	make migrate
