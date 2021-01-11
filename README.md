Footprints
==========

[![Actions Status](https://github.com/ccnmtl/footprints/workflows/build-and-test/badge.svg)](https://github.com/ccnmtl/footprints/actions)

Footprints is a project to develop a database that tracks individual books through time and space to uncover patterns of trade and learning throughout the Jewish communities of Europe, Asia and the Americas during the modern period.


TECHNICAL REQUIREMENTS
------------
Python 3
Postgres  
SOLR 3+
Celery 3


INSTALLATION
--------------
[See our installation docs on the wiki](https://github.com/ccnmtl/footprints/wiki/Installation)

DOCKER-COMPOSE
--------------

If you have docker-compose installed, you can do:

    $ make build
    $ docker-compose run web migrate   # to set up database schema
    $ docker-compose up
