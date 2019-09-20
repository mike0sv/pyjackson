==============
Type Hierarchy
==============

If you have a hierarchy of types and you want to be able to deserialize them using base type, you need
to register your base type with :func:`~pyjackson.decorators.type_field` decorator. First argument is a name of
class field, where you will put aliases for child types.

.. literalinclude:: ../../examples/type_hierarchy.py
   :linenos:
   :language: python
..
