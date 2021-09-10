====================
Development Guide
====================

Design
===============

Since it is just a wrapper, the wrapped API names and arguments should follow Flowdock API document.

To make it reusable unlike invoking Curl,
things such as API tokens should be cached for further operations that user care about,
like send or edit a message.

Wrapped API response should keep original response not to be modified,
so that user can learn what Flowdock exactly does by trial and error.

To reduce unexpected response due to user typo, wrapped API should validate supported parameters;
in the case of integration, the parameters in the nest JSON payload of a HTTP request should be validate, too.

Implementation
===============

To make it simple, consider the form::

    cache(token and URI arguments).operate(parameters and values)

Since it only requires namespace, implement callable with ``SimpleNamespace``
and nested function to share cached values, and implement non-callable with Python syntax ``class``.

To validate supported parameters, restrict the parameter names following origin API document,
and verify the parameter names for ``TypeError``.

For easy to debug, use f-string to represent URI patterns,
and use assertion to represent origin API response including status code and response payload.

To implement Server-Sent Events, simply follow W3C document instruction.

Testing
===============

All test cases are listed in README.rst and in doctest format.
Invoke built-in ``doctest`` module to execute test cases.

Most of all test cases are built on Flowdock services, require real API token and channels,
thus one might have to adjust test data for test environment.
At least, they can be executed repeatedly.

Publishing
===============

``README.rst`` treated as both user guide and landing page contains:

-   Releasd version, license, and so on.
-   Purpose, features, and usage.

``flowdock.py`` contains source code, real package status, and development guide in comment:

-   Version number
-   Design, implementation, testing, and publishing

Releases on PyPI are referred to PyPA tutorial `Packaging Python Projects`_ and leveraging ``twine``.
Below shows how to test publishing onto TestPyPI:

.. _`packaging python projects`: https://packaging.python.org/tutorials/packaging-projects/

.. code:: sh

    $ ls setup.py
    setup.py
    $ rm -r dist ; python setup.py sdist bdist_wheel
    $ twine check dist/*.whl
    $ twine upload --user=${user} --password=${password} --repository-url https://test.pypi.org/legacy/ 'dist/*'

.. WARNING:: MUST avoid version collision, which is no way to solve even deleting it on PyPI/TestPyPI.

Release process:

1.  Merge development branch to master
#.  Review hard-coded information in ``setup.py``
#.  Bump version number in ``flowdock.py``
#.  Upload to TestPyPI for test
#.  Commit with template "Bumped version to v0.0"
#.  Upload to PyPI
#.  Tag commit and push to Github
