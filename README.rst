====================
Flowdock API wrapper
====================

:Official API Document: https://www.flowdock.com/api


This API wrapper aim to summarize Flowdock API usage with intuitive implementation,
so that creating a chatbot, Flowdock integration, or monitor, are going to be simpler.

The following content describes `prior knowledge`_ and the `API wrapper usage`_.


.. new structure of the document, aka outline:

    A few parts:
        PERSONAL_API_TOKEN for identical user and further operations
        FLOW_TOKEN for external services bound to a flow channel
        Monitor -- based on identical user to handle server-sent event

    Every part provides keywords reference
    Every part starts with a feature overview and then introduce wrapped API usage with examples
    Finally summarize terminology; no need to provide whole references in one place



Prior Knowledge
====================

.. what basic API can do, require personal token
.. what integration API can do, require flow token for external service
    .. https://www.flowdock.com/oauth/applications
.. what monitor API can do
.. terminology: personal token, flow token, external service, server-sent event


.. _`API wrapper usage`:

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

.. code:: python

    >>> import flowdock
    >>> client = flowdock.connect(token=PERSONAL_API_TOKEN)

With the client, you can "join" the different channels with the same client.

.. code:: python

    >>> flow = client(org='hpe', flow='apua-flow')
    >>> private = client(uid=336968)

The :code:`uid` above is "user ID", which can be found in the tail of a private channel URI.

You can get UID by user's display name ("Display name" field in `Edit profile`_ page) as below.

.. _`edit profile`: https://www.flowdock.com/account/edit

.. code:: python

    >>> client.get_uid(name='Ray_')
    336968

For convenience, you can join a channel in one line:

.. code:: python

    >>> flow = flowdock.connect(token=PERSONAL_API_TOKEN, org='hpe', flow='apua-flow')
    >>> private = flowdock.connect(token=PERSONAL_API_TOKEN, uid=336968)

Also, you can simply give user's display name to get UID and then join the private channel in one line:

.. code:: python

    >>> private = flowdock.connect(token=PERSONAL_API_TOKEN, name='Ray_')

Connecting Flowdock with flow token is similar with personal API token;
the flow token bound to an individual flow is not required to specify flow.

.. code:: python

    >>> external_service = flowdock.connect(flow_token=FLOW_TOKEN)


Message
------------------------------

To send message in a flow, invoke :meth:`send` of the channel.

.. code:: python

    >>> msg_id = flow.send('a message')['id']

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

    >>> msg_id = private.send('a message')['id']
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
    >>> msg_id = flow.upload(file_path)['id']
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
    >>> msg_id = private.upload(file_path)['id']
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

To send a message with tags in a flow, set keyword argument ``tags`` to :meth:`send`.

.. code:: python

    >>> msg_id = flow.send('@team, ref here: http://docs.python.org', tags=['ref'])['id']
    >>> flow.show(msg_id)['tags']
    ['ref', ':user:team', ':url']

To override the tags of an existing message, set keyword argument ``tags`` to :meth:`edit`.
In this case, you don't have to be the author.

.. code:: python

    >>> flow.edit(msg_id, tags=['ref', ':user:team', 'important', ':url'])
    >>> flow.show(msg_id)['tags']
    ['ref', ':user:team', 'important', ':url']

You can edit both content and tags at the same time; in this case, you have to be the author.

.. code:: python

    >>> flow.edit(msg_id, '@team, read ref here: http://docs.python.org', tags=['ref', ':user:team', ':url'])
    >>> msg = flow.show(msg_id)
    >>> msg['content']
    '@team, read ref here: http://docs.python.org'
    >>> msg['tags']
    ['ref', ':user:team', ':url']


The tags prefixed with colon, like ``:user:team`` and ``:url`` above, are used on web page display.

When sending a new message, those special tags would be generated by backend;
in addition, backend eliminates duplicated tags and not change the order of tags.
An example of simply adding and removing tags is as below:

.. code:: python

    >>> tags = flow.show(msg_id)['tags']
    >>> tags
    ['ref', ':user:team', ':url']

    >>> tags += ['ref', 'python']
    >>> flow.edit(msg_id, tags=tags)
    >>> flow.show(msg_id)['tags']
    ['ref', ':user:team', ':url', 'python']

    >>> tags.remove('python')
    >>> flow.edit(msg_id, tags=tags)
    >>> flow.show(msg_id)['tags']
    ['ref', ':user:team', ':url']

It is supported in private channels as well.

.. code:: python

    >>> msg_id = private.send('ref here: http://docs.python.org', tags=['ref'])['id']
    >>> private.show(msg_id)['tags']
    [':unread:336968', 'ref', ':url']

    >>> private.edit(msg_id, tags=[':unread:336968', 'ref', 'resources', ':url'])
    >>> private.show(msg_id)['tags']
    [':unread:336968', 'ref', 'resources', ':url']


Emoji
------------------------------

Unfortunately, invoking :meth:`send` and :meth:`edit` to set emoji doesn't work;
Flowdock doesn't provide API for emoji, either.

A possible solution is emulating browser behavior to login with password, create web socket connection,
and then communicate with Flowdock server to ask change emoji.
It is too complicated, besides, user should not provide their password on chatbot;
that's why this library does not provide emoji support, either.


Thread
------------------------------

Every message sent in a flow has a thread ID;
to send message onto the thread, set keyword argument ``thread_id`` to :meth:`send`.

.. code:: python

    >>> msg1 = flow.send('Thread start')
    >>> msg2 = flow.send('A message in the thread', thread_id=msg1['thread_id'])
    >>> assert msg1['thread_id'] == msg2['thread_id']

Like emoji, invoking :meth:`edit` to re-thread a sent message doesn't work;
Flowdock doesn't provide API for re-threading, either.


Integration
------------------------------

.. image:: Flowdock\ Inbox.png
    :alt: Flowdock Inbox overview

Flowdock can integrate external services, e.g. Trello, onto Flowdock Inbox,
so that you can track item status, user activities, and discussion on the item.

Refer to Flowdock API documents below to understand the relationship between items and Flowdock threads,
and activities/discussions of an items.

Getting started:
https://www.flowdock.com/api/integration-getting-started#/getting-started

The components of an integration message:
https://www.flowdock.com/api/integration-getting-started#/components-of-a-message

Message types ("activity" and "discussion"):
https://www.flowdock.com/api/integration-getting-started#/message-types

Authorize your app with OAuth:
https://www.flowdock.com/api/production-integrations#/oauth2-authorize


Present an External Service Item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Those data maitained on the external servicesa are treated as items, every item has its ID and name, as shown below:

.. code:: python

    >>> item_id = 'ITEM-01'
    >>> item = {'title': 'Item 01'}

To present a user activity or discussion on the item requires define a user first.

.. code:: python

    >>> ray = {'name': 'Ray'}

With given ``thread`` for item and ``author`` for user, you can present an activity or discussion by :meth:`present`.
To present an activity, it requires only ``title`` for the activity description;
to present a discusion, it requires not only ``title`` for the description of discussion itself
(e.g. "comment") but also ``body`` for the discussion content.

.. code:: python

    >>> external_service.present(item_id, author=ray, title='created item', thread=item)
    >>> external_service.present(item_id, author=ray, title='commented', body='The comment', thread=item)

The expected result is as below.
Note that "ExternalService" shown in the figure is the integration name rather than the external service name,
thus it is recommended to set integration name the same as external service name.

.. image:: basic\ expected\ result.png
    :alt: basic expected result shows the presented item name, a user created item, and discussion

Activities is just like the item history,
therefore, each updating item operation should be presented with an activity.

If a item has been presented before and nothing changed, then it can be presented with only item id,
for example, discussion.

.. code:: python

    >>> external_service.present(item_id, author=ray, title='commented', body='More comment')

In the other side, the items, which aren't presented before and don't have both activites and discussion
after integration added, are not shown in Flowdock.


Check Presented Items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After presenting an activity or discussion, Flowdock API will not return the resource ID of activity or discussion.
A workaround is invoking :meth:`list` to find the latest activity or discussion event immediately.

.. code:: python

    >>> external_service.present(item_id, author=ray, title='commented', body='Comment again')
    >>> flow.list(limit=1).pop()['body']
    'Comment again'

If one considers there are meesages sent during presenting and checking, a solution is restricting the conditions.
However, it requires to determine which events it presented -- activity or discussion.

.. code:: python

    >>> external_service.present(item_id, author=ray, title='touched item')
    >>> external_service.present(item_id, author=ray, title='commented', body='I just touch the item')
    >>> flow.list(event='activity', limit=1).pop()['title']
    'touched item'
    >>> flow.list(event='discussion', limit=1).pop()['body']
    'I just touch the item'

Final solution is the most stable way, but a little complicated.
First, ``thread`` allow an optional key ``external_url`` which means the item URI actually.
Set it before sending, then filter it from threads.
The last event, no matter it is activity or discussion, should be the one you just send.

.. code:: python

    >>> uri = f'https://external.service/item/{item_id}'
    >>> item['external_url'] = uri
    >>> external_service.present(item_id, author=ray, title='touched item', thread=item)
    >>> #flow.thread()  # filter and ...

An important thing is, ``thread_id`` maps to item ID one-to-one, but has not the same value with item ID.
To retrieve item ID from thread, it is recommanded to set key ``external_url`` everytime,
see the example in `Construct author and thread`_.


Tag, Reply, and Delete a Presented Item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flowdock allows user to tag and reply an presented item, just like tag and reply a message.

.. code:: python

    >>> disc = flow.list(event='discussion', limit=1).pop()
    >>> flow.edit(disc['id'], tags=['idea'])  # tag the discussion
    >>> msg = flow.send('Reply the other idea', thread_id=disc['thread_id'])  # reply the discussion

Flowdock allows user to delete an presented item, too, just like delete a message. [*]_ [*]_

.. code:: python

    >>> flow.delete(disc['id'])
    >>> flow.show(disc['id'])
    Traceback (most recent call last):
      ...
    AssertionError: (404, b'{"message":"not found"}')

.. [*] If all activities/discussions are deleted, the thread of item will be hidden on Flowdock.
       However, it can still found by thread API.

.. [*] It seems anyone in the channel has privilege to delete activities and discussions.
       If so, it is dangerous because that deleted activities or discussions are hard to retrieve again.
       Moreover, in general, there is no need to delete them.


Construct ``author`` and ``thread``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In `Present an External Service Item`_, an example shows how to construct data,
which has some disadvantages during development:

-   Don't know which keys are necessary.
-   Don't remember the name of the keys.
-   May have typo not found until verifying on browser.

One can know which names are required by :meth:`present` already:

.. code:: python

    >>> help(external_service.present)
    Help on function present in module flowdock:
    <BLANKLINE>
    present(id, author, title, body=None, thread=None)
    <BLANKLINE>

Here, this wrapper provides constructors for data structure hints.

.. code:: python

    >>> from flowdock import constructors as new
    >>> help(new.author)
    Help on function author in module flowdock:
    <BLANKLINE>
    author(name, avatar=None)
    <BLANKLINE>
    >>> ray = new.author('Ray', avatar='http://somewhere.public/ray.png')
    >>> item = new.thread('Item 01')

For item description, ``thread`` data structure is complex. See example below. [*]_ [*]_

The origin data:

.. code:: python

    >>> item = {
    ...     'title': 'Item 01',
    ...     'external_url': 'https://external.service/item/ITEM-01',
    ...     'body': '<strong>The detail of the item here....</strong>',
    ...     'fields': [{'label': 'a', 'value': '1'}, {'label': '<a>b</a>', 'value': '<a>2</a>'}],
    ...     'status': {'color': 'green', 'value': 'TODO'},
    ...     'actions': [
    ...         {
    ...             "@type": "ViewAction",
    ...             "name": "Diff",
    ...             "url": "https://github.com/flowdock/component/pull/42/files",
    ...         },
    ...         {
    ...             '@type': 'UpdateAction',
    ...             'name': 'Assign to me',
    ...             'target': {
    ...                 '@type': 'EntryPoint',
    ...                 'urlTemplate': 'https://external.service/item/ITEM-01?assign=me',
    ...                 'httpMethod': 'POST',
    ...             },
    ...         },
    ...     ],
    ... }

By constrcutors:

.. code:: python

    >>> item_id = 'ITEM-01'
    >>> uri = f'https://external.service/item/{item_id}'
    >>> item = new.thread(
    ...     'Item 01',
    ...     external_url = uri,
    ...     body = '<strong>The detail of the item here....</strong>',
    ...     fields = [new.field(label='a', value='1'), new.field(label='<a>b</a>', value='<a>2</a>')],
    ...     status = new.status(color='green', value='TODO'),
    ...     actions = [
    ...         {
    ...             "@type": "ViewAction",
    ...             "name": "Diff",
    ...             "url": "https://github.com/flowdock/component/pull/42/files",
    ...         },
    ...         {
    ...             '@type': 'UpdateAction',
    ...             'name': 'Assign to me',
    ...             'target': {
    ...                 '@type': 'EntryPoint',
    ...                 'urlTemplate': f'{uri}?assign=me',
    ...                 'httpMethod': 'POST',
    ...             },
    ...         },
    ...     ],
    ... )

Supported status colors are as below; constructor ``status`` could validate the supported colors.

.. code:: python

    >>> item['status'] = new.status(color='not supported color', value='...')
    Traceback (most recent call last):
    ...
    TypeError: valid colors: black, blue, cyan, green, grey, lime, orange, purple, red, yellow

About ``actions``, refer to pages of Flowdock API documents for more information:

       -    https://www.flowdock.com/api/thread-actions
       -    https://www.flowdock.com/api/how-to-create-bidirectional-integrations

.. [*] There is no further constructor for ``actions`` because its data structure is flexible
       and would be bound to external services just like ``external_url``.

.. [*] ``UpdateAction`` defines how Flowdock send HTTP requests to the external service.
       It will not work if external services are in private network;
       in this case, consider ``ViewAction`` for workaround.
