==========
Quickstart
==========

To use PyJackson in a project, define a class with type hinted constructor arguments

.. literalinclude:: ../../examples/quickstart.py
   :linenos:
   :language: python
   :lines: 6-9

Now you are able to serialize instance of your class to dict and back with
:func:`~pyjackson.serialize` and :func:`~pyjackson.deserialize`

.. literalinclude:: ../../examples/quickstart.py
   :linenos:
   :language: python
   :lines: 12-15
..

It also works with nested structures and supports `typing` module generic annotations

.. literalinclude:: ../../examples/quickstart.py
   :linenos:
   :language: python
   :lines: 18-25
..

This code can be found in `examples/quickstart.py`
