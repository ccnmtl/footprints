APP=footprints
JS_FILES=media/js/app/ media/js/xeditable
MAX_COMPLEXITY=7
PY_DIRS=$(APP)
FLAKE8_IGNORE=W605

all: jenkins

include *.mk

test-travis: $(PY_SENTINAL)
	$(MANAGE) test --settings=$(APP).settings_travis

travis: check flake8 test-travis eslint bandit
