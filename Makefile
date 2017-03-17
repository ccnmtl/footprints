APP=footprints
JS_FILES=media/js/app/ media/js/xeditable
MAX_COMPLEXITY=7
PY_DIRS=$(APP) viaf

all: eslint jenkins

include *.mk

eslint: $(JS_SENTINAL)
	$(NODE_MODULES)/.bin/eslint $(JS_FILES)

.PHONY: eslint
