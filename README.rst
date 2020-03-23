========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor|
        | |coveralls|
        | |codeclimate|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/pyjackson/badge/?style=flat
    :target: https://readthedocs.org/projects/pyjackson
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/mike0sv/pyjackson.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/mike0sv/pyjackson

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/mike0sv/pyjackson?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/mike0sv/pyjackson

.. |coveralls| image:: https://coveralls.io/repos/mike0sv/pyjackson/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/github/mike0sv/pyjackson


.. |codeclimate| image:: https://codeclimate.com/github/mike0sv/pyjackson/badges/gpa.svg
    :alt: CodeClimate Quality Status
    :target: https://codeclimate.com/github/mike0sv/pyjackson

.. |version| image:: https://img.shields.io/pypi/v/pyjackson.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/pyjackson

.. |commits-since| image:: https://img.shields.io/github.com/commits-since/mike0sv/pyjackson/v0.0.25.svg
    :alt: Commits since latest release
    :target: https://github.com/mike0sv/pyjackson/compare/v0.0.25...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/pyjackson.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/pyjackson

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/pyjackson.svg
    :alt: Supported versions
    :target: https://pypi.org/project/pyjackson

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/pyjackson.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/pyjackson

.. end-badges

PyJackson is a serialization library based on type hinting

Example
==========

Just type hint `__init__` and you are ready to go::

    import pyjackson


    class MyPayload:
        def __init__(self, string_field: str, int_field: int):
            self.string_field = string_field
            self.int_field = int_field


    pyjackson.serialize(MyPayload('value', 10))  # {'string_field': 'value', 'int_field': 10}

    pyjackson.deserialize({'string_field': 'value', 'int_field': 10}, MyPayload)  # MyPayload('value', 10)

..

More features and examples `here
<https://pyjackson.readthedocs.io/en/latest/usage/index.html>`_ and in examples dir.



Installation
============

::

    pip install pyjackson

Documentation
=============


https://pyjackson.readthedocs.io/


Development
===========

To run all tests run::

    tox

..

Licence
=======

* Free software: Apache Software License 2.0
