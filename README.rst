====================
Flowdock API wrapper
====================

|PyPI Release Version| |License| |Supported Python Distro|

.. |PyPI Release Version| image:: https://img.shields.io/pypi/v/flowdock-api-wrapper?color=blue&label=PyPI&logo=python&logoColor=white
    :target: https://pypi.org/project/flowdock-api-wrapper/
.. |License| image:: https://img.shields.io/github/license/apua/flowdock?color=blue&label=License
    :target: https://github.com/apua/flowdock/blob/main/LICENSE
.. |Supported Python Distro| image:: https://img.shields.io/pypi/pyversions/flowdock-api-wrapper?color=blue&label=Python
    :target: https://pypi.org/project/flowdock-api-wrapper/

This API wrapper provides methods with **intuitive** implementation to make development simpler.

With Flowdock API, developers are able to:

Create chatbots
 .. code:: python

    >>> import flowdock
    >>> flow = flowdock.connect(token=TOKEN, org='apua', flow='main')
    >>> msg = flow.send('Message')  # send a message
    >>> thread = flow.thread(msg['thread']['id'])
    >>> reply = thread.send('Reply')  # reply the message
    >>> flow.list(limit=1)['content']  # get last message content
    'Reply'

Integrate external services
 .. code:: python

    >>> from flowdock import constructors as new
    >>> apua = new.author('Apua', avatar='http://gravatar.com/apua.jpg')
    >>> item = new.thread(
    ...     'Item 42',
    ...     external_url = 'https://external.service/item/42',
    ...     body = '<strong>The detail of Item 01</strong>',
    ...     fields = [
    ...         new.field(label='Project', value='F.A.W.'),
    ...         new.field(label='<em>Creator</em>', value='<em>Apua</em>'),
    ...     ],
    ...     status = new.status(color='green', value='WIP'),
    ... )
    >>> import flowdock
    >>> serivce = flowdock.connect(flow_token=FLOW_TOKEN)
    >>> service.present('42', apua, 'created item 42', item)

Monitor Flowdock flows
 .. code:: python

    >>> import flowdock
    >>> flow = flowdock.connect(token=TOKEN, org='apua', flow='main')
    >>> ev = next(flow.events())
    >>> ev['content'])
    'New message!!'


How to Install
==============

This package is available on PyPI:

.. code:: console

    $ pip install flowdock-api-wrapper


How to Use
==========

The `reference`_ is available to detail the library usage.

It also summarizes the usage of Flowdock API
while the wrapped methods map to the API directly.

Please refer to `reference`_ for further usage.

.. _`reference`: https://github.com/apua/flowdock/blob/main/doc/ref.rst


How to Contribute
=================

To contribute the package, refer to `development guide`_,
which decribe the design, implementation, and maintenance.

.. _`development guide`: https://github.com/apua/flowdock/blob/main/doc/dev.rst
