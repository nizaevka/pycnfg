Quick Start
===========

.. contents:: **Contents**
    :depth: 1
    :local:
    :backlinks: none


Start
~~~~~

To create any object, we need to specify initial state and steps to apply on.
Pycnfg offers pattern to pipeline-wise code execution, that naturally allows
to control all parameters via single configuration dictionary.


.. literalinclude:: /../../examples/simplest/conf.py
   :language: python
   :lineno-match:

:github:`github repo </examples/simplest>`

There are could be arbitrary number of sections/configurations.
Cross-configurations interaction goes through `objects` storage.


Next
~~~~

For deeper understanding please follow `Concepts <Concepts.html>`_.

For detailed examples `Examples <Examples.html>`_.


