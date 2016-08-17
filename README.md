Footprints
==========

[![Build Status](https://travis-ci.org/ccnmtl/footprints.svg?branch=master)](https://travis-ci.org/ccnmtl/footprints)

Footprints is a project to develop a database that tracks individual books through time and space to uncover patterns of trade and learning throughout the Jewish communities of Europe, Asia and the Americas during the modern period.


REQUIREMENTS
------------
Python 2.7  
Postgres  


DOCKER-COMPOSE
--------------

If you have docker-compose installed, you can do:

    $ make build
    $ docker-compose run web migrate   # to set up database schema
    $ docker-compose up
