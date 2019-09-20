====================
Custom Serialization
====================

If you want custom serialization logic for one of your class, or if you need to serialize external types with no type
hints, you can implement custom serializer for them. Serializer is bound to the type you register and will be used when
this type is encountered.

For example, you have class without type hints, or `__init__` differ from actual fields. Just implement StaticSerializer

.. literalinclude:: ../../examples/custom_serialization.py
   :linenos:
   :language: python
   :lines: 7-21
..

Now you can serialize External

.. literalinclude:: ../../examples/custom_serialization.py
   :linenos:
   :language: python
   :lines: 24-25
..

Like with simple types, it can be used in nested structures

.. literalinclude:: ../../examples/custom_serialization.py
   :linenos:
   :language: python
   :lines: 28-34
..

If you need to parametrize yor serializer, you can implement generic Serializer, adding your parameters to serializers
`__init__`. For example, you want to serialize lists of certain size with same values.

.. literalinclude:: ../../examples/custom_serialization.py
   :linenos:
   :language: python
   :lines: 37-56
..

You can also use serializers in type hints

.. literalinclude:: ../../examples/custom_serialization.py
   :linenos:
   :language: python
   :lines: 59-65
..


You can find this code in `examples/custom_serialization.py`
