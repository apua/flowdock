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


Authentication and Channel
------------------------------

To access resources of private channel/flows/external service integrations, Flowdock provides 2 kinds of tokens:

-   `Personal API token` -- as a user to access private channels and flows
-   `Flow token` -- as an external service integration to access inbox

For example, assume keys are stored in a Python file, say `test_tokens.py`.

.. code:: python

    >>> from test_tokens import PERSONAL_API_TOKEN, FLOW_TOKEN

To connect Flowdock with `personal API token`, simply invoke `connect` function to initialize a "client".
Then you can "join" the different channels with the same client.

.. code:: python

    >>> import flowdock
    >>> client = flowdock.connect(token=PERSONAL_API_TOKEN)
    >>> flow = client(org='hpe', flow='apua-flow')
    >>> private = client(uid=336968)

The `UID` above is "user ID", which can be found in the tail of a private channel URI.

You can also get `UID` by user's display name. [*]_

.. code:: python

    >>> client.get_uid(name='Ray_')
    336968

For convenience, you can join a channel in one line:

.. code:: python

    >>> flow = flowdock.connect(token=PERSONAL_API_TOKEN, org='hpe', flow='apua-flow')
    >>> private = flowdock.connect(token=PERSONAL_API_TOKEN, uid=336968)
    >>> private = flowdock.connect(token=PERSONAL_API_TOKEN, name='Ray_')

Connecting Flowdock with `flow token` is similar with personal API token;
since the flow token is bound to an individual flow, it is not required to specify flow.

.. code:: python

    >>> integration = flowdock.connect(flow_token=FLOW_TOKEN)


Message
------------------------------

To send message in a flow, invoke `send` methods of the channel.

.. code:: python

    >>> msg_id = flow.send('a message')

Invoke `edit` and `delete` methods to edit and delete specified messages;
the `get` method can be used to verify the messages.

.. code:: python

    >>> flow.show(msg_id)['content']
    'a message'
    >>> flow.edit(msg_id, 'an edit message')
    >>> flow.show(msg_id)['content']
    'an edit message'
    >>> flow.delete(msg_id)
    >>> flow.show(msg_id)['content']
    ''

To send, edit, delete, and get message in a private channel are as well.

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

.. upload, download


Tag
------------------------------

.. send, edit


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


Get UID by Display Name
------------------------------

.. >>> client.get_uid('Ray_')
.. 336968
.. >>> ray = client(336968)
