APP=footprints
JS_FILES=media/js/app/ media/js/xeditable
MAX_COMPLEXITY=7
PY_DIRS=$(APP) viaf
FLAKE8_IGNORE=W605

all: jenkins

include *.mk

