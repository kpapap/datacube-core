Database Setup
**************

.. attention::

    You must have a properly configured Postgres installation for this to work. If you have a fresh install of Postgres
    on Ubuntu then you may want to configure the ``postgres`` user password to `complete the postgres setup <https://help.ubuntu.com/community/PostgreSQL>`_

Install PostgreSQL
==================

Please refer to the `PostgreSQL <https://www.postgresql.org>`_ documentation on how to install and configure it.

Create Database
===============

If you have existing Postgres authentication:
::

    createdb datacube

or specify connection details manually:
::

    createdb -h <hostname> -U <username> datacube

.. note::

    You can also delete the database by running ``dropdb datacube``. This step is not reversible.

.. _create-configuration-file:

Create Configuration File
=========================

Datacube looks for a configuration file in ~/.datacube.conf or in the location specified by the ``DATACUBE_CONFIG_PATH`` environment variable. The file has this format::

    [datacube]
    # One config file may contain multiple named sections providing multiple configuration environments.
    # The section named "datacube" (or "default") is used if no environment is specified.

    # index_driver is optional and defaults to "default" (the default Postgres index driver)
    index_driver: default

    # The remaining configuration entries are for the default Postgres index driver and
    # may not apply to other index drivers.
    db_database: datacube

    # A blank host will use a local socket. Specify a hostname (such as localhost) to use TCP.
    db_hostname:
    
    # Port is optional. The default port is 5432.
    # db_port:

    # Credentials are optional: you might have other Postgres authentication configured.
    # The default username otherwise is the current user id.
    # db_username:
    # db_password:

    [test]
    # A "test" environment that accesses a separate test database.
    index_driver: default
    db_database: datacube_test

    [null]
    # A "null" environment for working with no index.
    index_driver: null

    [local_memory]
    # A local non-persistent in-memory index.
    #   Compatible with the default index driver, but resides purely in memory with no persistent database.
    #   Note that each new invocation will receive a new, empty index.
    index_driver: memory

Uncomment and fill in lines as required.

Alternately, you can configure the ODC connection to Postgres using environment variables::

    DB_HOSTNAME
    DB_USERNAME
    DB_PASSWORD
    DB_DATABASE

To configure a database as a single connection url instead of individual environment variables::
    
    export DATACUBE_DB_URL=postgresql://[username]:[password]@[hostname]:[port]/[database]

Alternatively, for password-less access to a database on localhost::

    export DATACUBE_DB_URL=postgresql:///[database]

Further information on database configuration can be found `here <https://github.com/opendatacube/datacube-core/wiki/ODC-EP-010---Replace-Configuration-Layer>`__.
Although the enhancement proposal details incoming changes in v1.9 and beyond, it should largely be compatible with the current behaviour, barring a few
obscure corner cases.

The desired environment can be specified:

1. in code, with the ``env`` argument to the ``datacube.Datacube`` constructor;
2. with the ``-E`` option to the command line ui;
3. with the ``$DATACUBE_ENVIRONMENT`` environment variable.

Initialise the Database Schema
==============================

The ``datacube system init`` tool can create and populate the Data Cube database schema ::

    datacube -v system init

.. click:: datacube.scripts.system:database_init

   :prog: datacube system
