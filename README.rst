====================
Flowdock API wrapper
====================

|PyPI Release Version| |Supported Python Distro|

.. |PyPI Release Version| image:: https://img.shields.io/pypi/v/flowdock-api-wrapper.svg?color=blue&label=PyPI&logo=python&logoColor=white
.. |Supported Python Distro| image:: https://img.shields.io/pypi/pyversions/flowdock-api-wrapper.svg?color=blue&label=Supported%20Python%20Distro

This API wrapper aim to **summarize** Flowdock API usage with **intuitive** implementation,
in order to make development simpler, like creating chatbots, integrating services, and monitoring Flowdock flows.

To install the wrapper, use ``pip`` or ``pipenv``:

.. code:: sh

    $ pip install flowdock-api-wrapper

To contribute the wrapper, refer to development guide in ``flowdock.py`` comment.

Following content focus on introduing the usage of this wrapper;
besides, since part of `Flowdock API Document`_ doesn't match current behavior,
there are notifications added in each sections.

.. _`Flowdock API Document`: https://www.flowdock.com/api

.. contents:: Contents
    :depth: 2

.. role:: func(literal)
.. role:: meth(literal)
.. role:: mod(literal)


Authentication and Channel
==============================

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

.. _`display name`:

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


Messaging
==============================

Send, Edit, and Delete a Message
----------------------------------------

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


Reply Message onto a Thread
----------------------------------------

Every message sent to a flow belongs to a thread:

.. code:: python

    >>> msg = flow.send('Thread start')
    >>> thread = msg['thread']

One can get thread ID of a message by two ways:

.. code:: python

    >>> thread_id = msg['thread']['id']
    >>> thread_id = msg['thread_id']

To send a message onto the thread, invoke :meth:`send` under :meth:`thread`.

.. code:: python

    >>> reply = flow.thread(thread_id).send('A message replied')


Tag a Message
----------------------------------------

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


Upload and Download a File
----------------------------------------

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


List Messages
----------------------------------------

.. _`List Messages -- Parameters`: https://www.flowdock.com/api/messages

To list messages with some constraints, invoke :meth:`list` with parameters defined in `List Messages -- Parameters`_.

A basic example is as below. Note that the result is always in *ascending* order.

.. cleanup

    >>> for m in flow.list(search='keyword'):
    ...     flow.delete(m['id'])

.. code:: python

    >>> msg = flow.send('a keyword here')

    >>> from time import sleep
    >>> sleep(1)  # wait a while

    >>> flow.list(search='keyword')[-1]['content']
    'a keyword here'

Although this Flowdock API is flexible to combine parameters, there are still rules hidden behind API.
After trial and error, we summarize two pattern here.


1. ``(search keywords) ∪ (match tags in mode) → skip N → limit N``
````````````````````````````````````````````````````````````````````````````````

For example below, it takes union of search results and tags matching results,
skip the newest some, then limit the first some. [*]_

.. cleanup

    >>> for m in flow.list(search='keyword', tags=['A', 'B'], tag_mode='or'):
    ...     flow.delete(m['id'])

.. code:: python

    >>> msg1 = flow.send('1. a keyword')
    >>> msg2 = flow.send('2. keywords', tags=['A'])
    >>> msg3 = flow.send('3. more keywords', tags=['A', 'B'])

    >>> verify = lambda L: print(*[i['content'][0] for i in L])
    >>> sleep(1)

    >>> verify(flow.list(search='keyword'))
    1
    >>> verify(flow.list(tags=['A', 'B']))
    3
    >>> verify(flow.list(tags=['A', 'B'], tag_mode='or'))
    2 3
    >>> verify(flow.list(search='keyword', tags=['A', 'B'], tag_mode='or'))
    1 2 3
    >>> verify(flow.list(search='keyword', tags=['A', 'B'], tag_mode='or', skip=1))
    1 2
    >>> verify(flow.list(search='keyword', tags=['A', 'B'], tag_mode='or', limit=1))
    3
    >>> verify(flow.list(search='keyword', tags=['A', 'B'], tag_mode='or', skip=1, limit=1))
    2

.. [*] ``tags`` can be either comma seperated string (as document described) or a list of string in fact.


2. ``(event type) ∩ (since ID - until ID) → sort [desc|asc] → limit N``
````````````````````````````````````````````````````````````````````````````````

For example below, it takes the results of matching event types greater than an ID and less than an ID,
then limit the first some or last some. [*]_ [*]_

.. code:: python

    >>> file_path = './README.rst'
    >>> msg1 = flow.upload(file_path)
    >>> msg2 = flow.upload(file_path)
    >>> msg3 = flow.upload(file_path)
    >>> msg4 = flow.send('file_path')
    >>> msg5 = flow.upload(file_path)

    >>> M = {msg1['id']: 1, msg2['id']: 2, msg3['id']: 3, msg4['id']: 4, msg5['id']:5}
    >>> verify = lambda L: print(*[M[m['id']] for m in L])
    >>> sleep(1)

    >>> verify(flow.list(since_id=msg1['id']))
    2 3 4 5
    >>> verify(flow.list(since_id=msg1['id'], until_id=msg5['id']))
    2 3 4
    >>> verify(flow.list(event='file', since_id=msg1['id']))
    2 3 5
    >>> verify(flow.list(event='file', since_id=msg1['id'], limit=1))
    5
    >>> verify(flow.list(event='file', since_id=msg1['id'], sort='asc', limit=1))
    2

.. [*] The parameter ``sort`` only works with parameter ``limit`` for changing behavior,
       and will not change the order of result.

.. [*] While delete an uploaded file, the response of "filtering last some" becomes incorrect,
       and will be recovered later about 5 minutes.

----

To list uploaded files, both ways below work:

.. code:: python

    >>> msgs = flow.list(tags=':file')
    >>> msgs = flow.list(event='file')

To list messages contains link or Email, there is a way as below:

.. code:: python

    >>> msgs = flow.list(tags=':url')

To list messages mentioned user with given `display name`_, for example, "@team":

.. code:: python

    >>> msgs = flow.list(tags='@team')


List Threads
----------------------------------------

In contrast to listing messages, the result of listing threads is always in *descending* order.

To list the threads under the flow, invoke :meth:`threads` (plural).

.. code:: python

    >>> thread = flow.threads(limit=1)[0]

API document list `parameters of listing flow threads`_, but not match the current Flowdock API.
In addition to parameter ``limit``, there are only other parameters ``until`` and ``since`` are supported.

.. code:: python

    >>> threads = flow.threads(since='2019-01-01T00:00:00Z', until='2019-12-01T00:00:00Z')

To list messages under a thread, invoke :meth:`list` under :meth:`thread` (singular) with given thread ID.

.. code:: python

    >>> msg = flow.thread(thread['id']).list(limit=1)[0]

.. _`parameters of listing flow threads`: `List Flow Threads`_

.. _`List Flow Threads`: https://www.flowdock.com/api/threads#/List


Integration
==============================

.. image:: https://github.com/apua/flowdock/raw/re-write/Flowdock%20Inbox.png
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
----------------------------------------

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

.. image:: https://github.com/apua/flowdock/raw/re-write/basic%20expected%20result.png
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
----------------------------------------

After presenting an activity or discussion, Flowdock API will not return the resource ID of activity or discussion.
A workaround is checking the latest sent message.

.. code:: python

    >>> external_service.present(item_id, author=ray, title='commented', body='No URI returned')

Since there may be newer message has been sent during checking the latest sent message,
it requires some restrictions to assure the last one is which you sent.

With no restriction, simply invoke :meth:`list` to get the last one:

.. code:: python

    >>> flow.list(limit=1).pop()['body']
    'No URI returned'

For example above, which present with a discussion, one can list only last discussion event,
or list content/body contains the string (obviously it does not work with activity):

.. code:: python

    >>> flow.list(event='discussion').pop()['body']
    'No URI returned'
    >>> flow.list(search='URI').pop()['body']
    'No URI returned'

The other workaround is more stable: presenting every thread with optional attribute ``external_url``
which means the item URI actually. With the URI, one can indentify the thread.
Since it is almost impossible multiple integration presenting the same item,
one can assure the last activity/discussion is sent by themselves.

.. code:: python

    >>> uri = f'https://external.service/item/{item_id}'
    >>> item['external_url'] = uri
    >>> external_service.present(item_id, author=ray, title='touched item', thread=item)
    >>> thread = next(t for t in flow.threads() if t['external_url']==uri)
    >>> flow.thread(thread['id']).list(event='activity').pop()['title']
    'touched item'


Tag, Reply, and Delete a Presented Item
----------------------------------------

Flowdock allows user to tag and reply an presented item, just like tag and reply a message.

.. code:: python

    >>> disc = flow.list(event='discussion', limit=1).pop()
    >>> flow.edit(disc['id'], tags=['idea'])  # tag the discussion
    >>> msg = flow.thread(disc['thread_id']).send('Reply the other idea')  # reply the discussion

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
----------------------------------------

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
    TypeError: got invalid color; supported colors are: ('black', 'blue', 'cyan', 'green', 'grey', 'lime', 'orange', 'purple', 'red', 'yellow')

About ``actions``, refer to pages of Flowdock API documents for more information:

       -    https://www.flowdock.com/api/thread-actions
       -    https://www.flowdock.com/api/how-to-create-bidirectional-integrations

.. [*] There is no further constructor for ``actions`` because its data structure is flexible
       and would be bound to external services just like ``external_url``.

.. [*] ``UpdateAction`` defines how Flowdock send HTTP requests to the external service.
       It will not work if external services are in private network;
       in this case, consider ``ViewAction`` for workaround.


Event Monitor
==============================

Based on `Server-Sent Events`_, `Flowdock streaming API`_ sends JSON content via ``data`` field of events,
and this API wrapper loads JSON content into Python dict.

To monitor a flow, invoke :meth:`events` returns an iterator.
An example that monitoring a flow and sending a message concurrently as below:

.. code:: python

    >>> import threading, time
    ...
    >>> def sleep_and_send_message():
    ...     time.sleep(1)
    ...     flow.send('1 second later')
    ...
    >>> threading.Thread(target=sleep_and_send_message).start()
    >>> e = next(flow.events())
    >>> e['content']
    '1 second later'

What will be sent via `Flowdock streaming API`_ is undocumented and really interesting.
For example, one can monitoring whether or not a user is typing.

.. _`flowdock streaming api`: https://www.flowdock.com/api/streaming
.. _`server-sent events`: https://www.w3.org/TR/2009/WD-eventsource-20090421/#event-stream-interpretation


Not Implemented
==============================

API wrapper of some resources are not implemented because they are rarely used. List below:

-   Flows
-   A thread
-   Private conversations
-   Users
-   Organizations
-   Sources
-   Invitations


Add Emoji onto a Message
----------------------------------------

Unfortunately, invoking :meth:`send` and :meth:`edit` to set emoji doesn't work;
Flowdock doesn't provide API for emoji, either.

A possible solution is emulating browser behavior to login with password, create web socket connection,
and then communicate with Flowdock server to ask change emoji.
It is too complicated, besides, user should not provide their password on chatbot;
that's why this library does not provide emoji support, either.


Re-thread a Message onto a Thread
----------------------------------------

Like emoji, invoking :meth:`edit` to re-thread a sent message doesn't work;
Flowdock doesn't provide API for re-threading, either.
