Changelog
=========

0.0.25 (2020-03-23)
-------------------------

* Support for int and float keys in dicts

0.0.24 (2020-02-22)
-------------------------

* Support for python 3.8

0.0.23 (2019-12-16)
-------------------------

* Fixed bug in subtype resolving

0.0.21 (2019-11-25)
-------------------------

* Fixed default type name

0.0.19 (2019-11-25)
-------------------------

* Allow subtype reregistration flag

0.0.18 (2019-11-22)
-------------------------

* Added support for full class path in type field (with importing logic)

0.0.17 (2019-11-21)
-------------------------

* Added Any support for serde skipping

0.0.16 (2019-11-15)
-------------------------

* Raise on subtype resolve error and fix for camel case forward ref resolving

0.0.15 (2019-11-11)
-------------------------

* Set class docstring and qualname of hierarchy root to be valid

0.0.14 (2019-11-05)
-------------------------

* Added decorator for camel case field renaming

0.0.13 (2019-11-03)
-------------------------

* Added decorator for field renaming

0.0.12 (2019-10-28)
-------------------------

* Fixed is_serializable for Field

0.0.11 (2019-10-28)
-------------------------

* Fixed is_serializable for Signature

0.0.10 (2019-10-16)
-------------------------

* Set class name and module of hierarchy root to be valid

0.0.9 (2019-10-09)
-------------------------

* Removed empty Serialzier __init__ method and fix for staticmethod in serializer

0.0.8 (2019-10-07)
-------------------------

* Changed is_collection to not include dict type

0.0.7 (2019-10-04)
--------------------------

* Added datetime.datetime serializer

0.0.6 (2019-10-02)
--------------------------

* Added Tuple[X, Y] and Tuple[X, ...] support

0.0.5 (2019-09-30)
--------------------------

* Fixed comparison of serializers

0.0.4 (2019-09-17)
--------------------------

* Added some examples and minor fixes

0.0.3 (2019-09-17)
--------------------------

* First release on PyPI.
