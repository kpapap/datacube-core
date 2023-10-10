Mac OSX Developer Setup
***********************

**Under construction**

Base OS: Mac OSX

This guide will setup an ODC core development environment and includes:

 - Anaconda python using conda environments to isolate the odc development environment
 - installation of required software and useful developer manuals for those libraries
 - Postgres database installation with a local user configuration
 - Integration tests to confirm both successful development setup and for ongoing testing
 - Build configuration for local ODC documentation


Required software
=================

Postgres:

    Download and install the EnterpriseDB distribution from `here <https://www.enterprisedb.com/downloads/postgres-postgresql-downloads>`_


.. include:: common_install.rst


You can now specify the database user and password for ODC integration testing. To do this::

    cp integration_tests/integration.conf ~/.datacube_integration.conf

Then edit the ``~/.datacube_integration.conf`` with a text editor and add the following lines, replacing ``<foo>`` with your username and ``<foobar>`` with the database user password you set above (not the postgres one, your ``<foo>`` one)::

    [datacube]
    db_hostname: localhost
    db_database: pgintegration
    index_driver: default
    db_username: <foo>
    db_password: <foobar>

    [experimental]
    db_hostname: localhost
    db_database: pgisintegration
    index_driver: postgis
    db_username: <foo>
    db_password: <foobar>


Verify it all works
===================

Install additional test dependencies::
    
    cd datacube-core
    pip install --upgrade -e '.[test]'
    
Run the integration tests::

    ./check-code.sh integration_tests

Note: if moto-based AWS-mock tests fail, you may need to unset all AWS environment variables.

Build the documentation::

    pip install --upgrade -e '.[doc]'
    cd docs
    pip install -r requirements.txt
    sudo apt install make
    sudo apt install pandoc
    make html

Then open :file:`_build/html/index.html` in your browser to view the Documentation.
