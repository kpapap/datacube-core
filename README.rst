Open Data Cube Core
===================

.. image:: https://github.com/opendatacube/datacube-core/workflows/build/badge.svg
    :alt: Build Status
    :target: https://github.com/opendatacube/datacube-core/actions

.. image:: https://codecov.io/gh/opendatacube/datacube-core/branch/develop/graph/badge.svg
    :alt: Coverage Status
    :target: https://codecov.io/gh/opendatacube/datacube-core

.. image:: https://readthedocs.org/projects/datacube-core/badge/?version=latest
    :alt: Documentation Status
    :target: http://datacube-core.readthedocs.org/en/latest/

Overview
========

The Open Data Cube Core provides an integrated gridded data
analysis environment for decades of analysis ready earth observation
satellite and related data from multiple satellite and other acquisition
systems.

Documentation
=============

See the `user guide <http://datacube-core.readthedocs.io/en/latest/>`__ for
installation and usage of the datacube, and for documentation of the API.

`Join our Slack <http://slack.opendatacube.org>`__ if you need help
setting up or using the Open Data Cube.

Please help us to keep the Open Data Cube community open and inclusive by
reading and following our `Code of Conduct <code-of-conduct.md>`__.

Requirements
============

System
~~~~~~

-  PostgreSQL 10+
-  Python 3.8+

Developer setup
===============

1. Clone:

   -  ``git clone https://github.com/opendatacube/datacube-core.git``

2. Create a Python environment for using the ODC.  We recommend `Mambaforge <https://mamba.readthedocs.io/en/latest/user_guide/mamba.html>`__ as the
   easiest way to handle Python dependencies.

::

   mamba env create -f conda-environment.yml
   conda activate cubeenv

3. Install a develop version of datacube-core.

::

   cd datacube-core
   pip install --upgrade -e .

4. Install the `pre-commit <https://pre-commit.com>`__ hooks to help follow ODC coding
   conventions when committing with git.

::

   pre-commit install

5. Run unit tests + PyLint

Install test dependencies using:
   
   ``pip install --upgrade -e '.[test]'``

If install for these fails, please lodge them as issues.
   
Run unit tests with:

   ``./check-code.sh``

   (this script approximates what is run by GitHub Actions. You can
   alternatively run ``pytest`` yourself). 

6. **(or)** Run all tests, including integration tests.

   ``./check-code.sh integration_tests``

   -  Assumes a password-less Postgres database running on localhost called

   ``pgintegration``

   -  Otherwise copy ``integration_tests/integration.conf`` to
      ``~/.datacube_integration.conf`` and edit to customise.

   - For instructions on setting up a password-less Postgres database, see
      the `developer setup instructions <https://datacube-core.readthedocs.io/en/latest/installation/setup/ubuntu.html#postgres-database-configuration>`__.


Alternatively one can use the ``opendatacube/datacube-tests`` docker image to run
tests. This docker includes database server pre-configured for running
integration tests. Add ``--with-docker`` command line option as a first argument
to ``./check-code.sh`` script.

::

   ./check-code.sh --with-docker integration_tests


To run individual tests in a docker container

::

    docker build --tag=opendatacube/datacube-tests-local --no-cache --progress plain -f docker/Dockerfile .

    docker run -ti -v $(pwd):/code opendatacube/datacube-tests-local:latest pytest integration_tests/test_filename.py::test_function_name


Developer setup on Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~

Building a Python virtual environment on Ubuntu suitable for development work.

Install dependencies:

::

    sudo apt-get update
    sudo apt-get install -y \
        autoconf automake build-essential make cmake \
        graphviz \
        python3-venv \
        python3-dev \
        libpq-dev \
        libyaml-dev \
        libnetcdf-dev \
        libudunits2-dev


Build the python virtual environment:

::

    pyenv="${HOME}/.envs/odc"  # Change to suit your needs
    mkdir -p "${pyenv}"
    python3 -m venv "${pyenv}"
    source "${pyenv}/bin/activate"
    pip install -U pip wheel cython numpy
    pip install -e '.[dev]'
    pip install flake8 mypy pylint autoflake black
