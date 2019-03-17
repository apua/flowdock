====================
Flowdock API wrapper
====================

:Official API Document: https://www.flowdock.com/api
:Official API Document Repository: https://github.com/flowdock/api-docs

The origin Flowdock API document is outdate.
This tool aim to be an intuitive wrapper summarizes the usage.


Usage
====================

.. contents:: Tabe of Contents
    :local:

.. role:: func(literal)
.. role:: meth(literal)
.. role:: mod(literal)


Authentication and Channel
------------------------------

To access resources of private channel/flows/external service integrations, Flowdock provides 2 kinds of tokens:

-   Personal API token -- As a user to access private channels and flows.
    A user can get personal API token from `API tokens`_ page.

-   Flow token -- As an external service integration to access inbox.
    It is generated after adding an integration onto a flow.

.. _`api tokens`: https://www.flowdock.com/account/tokens

Here, we assume keys are stored in a Python file, say :mod:`test_tokens.py`.

.. code:: python

    >>> from test_tokens import PERSONAL_API_TOKEN, FLOW_TOKEN

To connect Flowdock with personal API token, simply invoke :func:`connect` to initialize a "client".
Then you can "join" the different channels with the same client.

.. code:: python

    >>> import flowdock
    >>> client = flowdock.connect(token=PERSONAL_API_TOKEN)
    >>> flow = client(org='hpe', flow='apua-flow')
    >>> private = client(uid=336968)

The :code:`uid` above is "user ID", which can be found in the tail of a private channel URI.

You can also get UID by user's display name ("Display name" field in `Edit profile`_ page) as below.

.. _`edit profile`: https://www.flowdock.com/account/edit

.. code:: python

    >>> client.get_uid(name='Ray_')
    336968

For convenience, you can join a channel in one line:

.. code:: python

    >>> flow = flowdock.connect(token=PERSONAL_API_TOKEN, org='hpe', flow='apua-flow')
    >>> private = flowdock.connect(token=PERSONAL_API_TOKEN, uid=336968)
    >>> private = flowdock.connect(token=PERSONAL_API_TOKEN, name='Ray_')

Connecting Flowdock with flow token is similar with personal API token;
the flow token bound to an individual flow is not required to specify flow.

.. code:: python

    >>> integration = flowdock.connect(flow_token=FLOW_TOKEN)


Message
------------------------------

To send message in a flow, invoke :meth:`send` of the channel.

.. code:: python

    >>> msg_id = flow.send('a message')

To edit/delete a message, invoke :meth:`edit`/:meth:`delete`;
to verify the messages, invoke :meth:`get` to get message properties.

.. code:: python

    >>> flow.show(msg_id)['content']
    'a message'
    >>> flow.edit(msg_id, 'an edit message')
    >>> flow.show(msg_id)['content']
    'an edit message'
    >>> flow.delete(msg_id)
    >>> flow.show(msg_id)['content']
    ''

Those methods are supported in private channels as well.

.. code:: python

    >>> msg_id = private.send('a message')
    >>> private.show(msg_id)['content']
    'a message'
    >>> private.edit(msg_id, 'an edit message')
    >>> private.show(msg_id)['content']
    'an edit message'
    >>> private.delete(msg_id)
    >>> private.show(msg_id)['content']
    ''


File
------------------------------

To upload a file in a flow, invoke :meth:`upload` with the file path;
to download the file, get URI path by :meth:`show` and then invoke :meth:`download`.

.. code:: python

    >>> file_path = './README.rst'
    >>> msg_id = flow.upload(file_path)
    >>> msg_content = flow.show(msg_id)['content']
    >>> msg_content['file_name']
    'README.rst'
    >>> uri_path = msg_content['path']
    >>> bin_data = flow.download(uri_path)
    >>> flow.delete(msg_id)
    >>> flow.show(msg_id)
    Traceback (most recent call last):
      ...
    AssertionError: (404, b'{"message":"not found"}')

Those methods are supported in private channels as well.

.. code:: python

    >>> file_path = './README.rst'
    >>> msg_id = private.upload(file_path)
    >>> msg_content = private.show(msg_id)['content']
    >>> msg_content['file_name']
    'README.rst'
    >>> uri_path = msg_content['path']
    >>> bin_data = private.download(uri_path)
    >>> private.delete(msg_id)
    >>> private.show(msg_id)
    Traceback (most recent call last):
      ...
    AssertionError: (404, b'{"message":"not found"}')


Tag
------------------------------

To send a message with tags in a flow, set keyword argument ``tags`` to :meth:`send`;
to override the tags of an existing message, set keyword argument ``tags`` to :meth:`edit`.

.. code:: python

    >>> msg_id = flow.send('@team, ref here: http://docs.python.org', tags=['ref'])
    >>> flow.show(msg_id)['tags']
    ['ref', ':user:team', ':url']

    >>> flow.edit(msg_id, tags=['ref', ':user:team', 'important', ':url'])
    >>> flow.show(msg_id)['tags']
    ['ref', ':user:team', 'important', ':url']

.. tip:: You can edit one of content and tags, or both, in one time.

The tags prefixed with colon, like ``:user:team`` and ``:url`` above, are used on web page display.
When sending a new message, those special tags would be generated by backend.
In addition, backend eliminates duplicated tags and not change the order of tags.

An example of simply adding and removing tags is as below:

.. code:: python

    >>> tags = flow.show(msg_id)['tags']
    >>> tags
    ['ref', ':user:team', 'important', ':url']

    >>> tags += ['ref', 'python']
    >>> flow.edit(msg_id, tags=tags)
    >>> flow.show(msg_id)['tags']
    ['ref', ':user:team', 'important', ':url', 'python']

    >>> tags.remove('important')
    >>> tags.remove('python')
    >>> flow.edit(msg_id, tags=tags)
    >>> flow.show(msg_id)['tags']
    ['ref', ':user:team', ':url']

It is supported in private channels as well.

.. code:: python

    >>> msg_id = private.send('ref here: http://docs.python.org', tags=['ref'])
    >>> private.show(msg_id)['tags']
    [':unread:336968', 'ref', ':url']

    >>> private.edit(msg_id, tags=[':unread:336968', 'ref', 'resources', ':url'])
    >>> private.show(msg_id)['tags']
    [':unread:336968', 'ref', 'resources', ':url']


Emoji
------------------------------

.. flow only


Thread
------------------------------

.. reply (get thread id)  # `external_thread_id` ?


Present External Item
------------------------------

.. update item states w/wo item detail as a thread
.. describe item detail
.. reply onto item (both user and bot)


Monitor Flow
------------------------------


List
------------------------------


.. text search and tagged -- search x tags x tags_mode x skip x limit
.. file and activitie -- event x sort x since_id x until_id x limit
.. list threads and list messages in given thread
.. link and email
