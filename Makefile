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

docker-solr:
	docker run -d -v $(CURDIR)/solr/footprints:/opt/solr/server/solr/footprints -p 8983:8983 --name solr7 solr:7

docker-solr-clean:
	-docker stop solr7
	-docker rm solr7

docker-solr-shell:
	docker exec -it solr7 /bin/bash 


.PHONY: docker-solr docker-solr-clean docker-solr-shell 