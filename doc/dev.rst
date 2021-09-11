This guide notes things to know on development and maintenance.


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

All test cases are listed in `ref.rst`__ and in doctest format.
Invoke built-in ``doctest`` module to execute test cases.

__ ./ref.rst

Most of all test cases are built on Flowdock services, require real API token and channels,
thus one might have to adjust test data for test environment.
At least, they can be executed repeatedly.


Repository
===============

To keep the repository simple for simple project,
there are less items at the top of folder structure.

``LICENSE``
    Should be at the top of repository.

    The "year" inside means "the year of first publication of the work", doesn't have to be updated.
    Ref: https://www.copyrightlaws.com/copyright-symbol-notice-year/

``README.rst``
    The full description of pacakge in metadata and shown on PyPI,
    includes package version, license, introduction, and usage glance.

    All links inside README must be absoluted path.

    The badge images and hyperlinks should not bind to newest version.
    Instead, the image should be static and link to sepecified git tag every time.

``pyproject.toml``
    Set project metadata with build tool ``flit``.

    ``flit`` helps:

    -   to setup development environment by initializing ``pyproject.toml``,
        installing dependencies, and setting source code for edit mode.
    -   to package and publish source code to sdist and wheel.

    ``flit`` would not build anything such as compile C code or support build script.

    To publish a package, follow the workflow:

    #.  Update the version number and project metadata inside ``pyproject.toml``.
    #.  Update badges inside ``README.rst``.
    #.  Ensure commit merged to ``main`` branch.
    #.  Commit bumping version number.
    #.  Check build content by ``flit build`` and ``tar tvf dist/*``.
    #.  Publish by ``flit update``.
    #.  Tag commit by git tag.

    TestPyPI can help to verify the result on PyPI::

        FLIT_INDEX_URL=https://test.pypi.org/legacy/ FLIT_USERNAME=*** FLIT_PASSWORD=*** flit publish --no-setup --format=wheel

``src/``
    Stores source code ``flowdock.py``.

    There is a wrong convention in most Python projects that
    put module (e.g. ``flowdock/``) at the top of repository.

    The folders, such as "doc"/"build"/"dist", their name is repository-wise,
    thus source code should be in "src" rather than expose at the top.

    Another wrong convention is the usage of ``__version__``.

    The version number is project-wise, and is part of metadata.
    It could be put at the top of each source code, in comment, with license.
    But it should not a Python object.

``doc/``
    Collects documents and related media.

    It is worth to allocate a folder for them, because it is inappropriate
    to store them in source code docstring or comments.

Automation
===============

The preferred CI service is GitHub Actions.

On such minimal project, it is not worth to add things, such as linter, to CI.
It is not worth to automate tests for free trial Flowdock, either.

To update code, verify, bump version, and publish the package, we keep it manually
in order to avoid maintaining additional CI workflow.
