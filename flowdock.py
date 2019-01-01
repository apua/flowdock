r"""
Intuitive API wrapper
=====================

The wrapper keeps interaction with Python as simple as with Curl, but more intuitive.
If one can write a simple Curl command, then they can write one line in Python as well;
if one have to write a complex Curl command, then they can write clear code here.


Use `python -m doctest flowdock.py` to test
Use `python -m pydoc flowdock` to read document


TODO:

- organize `message` payload nicely
- organize `event` payload nicely
- reply specified thread
- support integration present and post


Usage
=====

Initialize and go into a private message or flow
------------------------------------------------

>>> import flowdock
>>> from token import PERSONAL_API_TOKEN

>>> client = flowdock.client(PERSONAL_API_TOKEN, 'hpe')
>>> client.get_uid('Ray_')
336968
>>> ray = client('Ray_')  # client(336968)
>>> cirrus = client(flow="cirrus")

>>> myflow = flowdock.client(token=PERSONAL_API_TOKEN, org='hpe', flow="apua-bot-1")

Send and edit private message
-----------------------------

>>> msg_id = ray.send('orig_content')
>>> ray.show(msg_id)['content']
'orig_content'
>>> ray.edit(msg_id, 'edited_content')
>>> ray.show(msg_id)['content']
'edited_content'
>>> ray.delete(msg_id)  # i.e. edit it as empty
>>> msg_id = ray.send('orig_content')

>>> msgs = ray.list(limit=30)
>>> msgs = ray.list(search="keyword1 keyword2 ...", skip=10)
>>> msgs = ray.list(tags=['a','b'],tag_mode='and')  # tag_mode := and | or

Send and edit flow message
--------------------------

>>> msg_id = myflow.send('orig_content')
>>> myflow.show(msg_id)['content']
'orig_content'
>>> myflow.edit(msg_id, 'edited_content')
>>> myflow.edit(msg_id, tags=['A______A'])
>>> myflow.show(msg_id)['content']
'edited_content'
>>> myflow.delete(msg_id)

>>> msg_id = myflow.send('@Ray_, content with tags', tags=['haha'])
>>> assert 'haha' in myflow.show(msg_id)['tags']
>>> myflow.edit(msg_id, tags=['nono'])
>>> assert 'haha' in myflow.show(msg_id)['tags']
>>> myflow.edit(msg_id, tags=['yes'], override_tags=True)
>>> assert 'haha' not in myflow.show(msg_id)['tags']
>>> myflow.delete(msg_id)

>>> msgs = myflow.list(limit=30)
>>> msgs = myflow.list(search="keyword1 keyword2 ...", skip=10)
>>> msgs = myflow.list(tags=['a','b'],tag_mode='and')  # tag_mode := and | or
>>> msgs = myflow.list(events='message')  # events := message | discussion | activity | file | status

Listen flow events
------------------

::
    for event in myflow.events():
        print(event.data)

>>> for i, event in enumerate(myflow.events()):
...     if i > 2:
...         break
"""

from collections import namedtuple
import json
import re
from typing import Union

import requests


Event = namedtuple('Event', ('data',))
PrivateConversation = namedtuple('PrivateConversation', ('show', 'send', 'delete', 'edit', 'list'))
Flow = namedtuple('Flow', ('show', 'send', 'delete', 'edit', 'list', 'events'))


def _private_conversation(auth, base, uid):
    """
    send: content -> IO msg_id
    show: msg_id -> IO Message
    delete: msg_id -> IO None
    edit: msg_id -> content -> IO None
    list: Options -> IO [Message]
    """
    def send(content):
        resp = requests.post(f'{base}/private/{uid}/messages', auth=auth, json={'event':'message','content':content})
        assert resp.status_code == 201, (resp.status_code, resp.json())
        msg_id = resp.json()['id']
        return msg_id

    def show(msg_id):
        resp = requests.get(f'{base}/private/{uid}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.json())
        msg = resp.json()
        return msg

    def delete(msg_id):
        resp = requests.delete(f'{base}/private/{uid}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200 and not resp.json(), (resp.status_code, resp.json())

    def edit(msg_id, content):
        resp = requests.put(f'{base}/private/{uid}/messages/{msg_id}', auth=auth, json={'content':content})
        assert resp.status_code == 200 and not resp.json(), (resp.status_code, resp.json())

    def list(**conditions):
        resp = requests.get(f'{base}/private/{uid}/messages', auth=auth, json=conditions)
        assert resp.status_code == 200, (resp.status_code, resp.json())
        msgs = resp.json()
        return msgs

    return PrivateConversation(*map(locals().__getitem__, PrivateConversation._fields))


def _flow(auth, base, org, flow):
    """
    send: content -> IO msg_id
    show: msg_id -> IO Message
    delete: msg_id -> IO None
    edit: msg_id -> content -> IO None
    list: Options -> IO [Message]

    present: flow_token -> ItemInfo -> Item

    events: IO [Event]
    """
    def send(content, tags=None):
        resp = requests.post(f'{base}/flows/{org}/{flow}/messages', auth=auth, json={'event':'message','content':content,'tags':tags})
        assert resp.status_code == 201, (resp.status_code, resp.json())
        msg_id = resp.json()['id']
        return msg_id

    def show(msg_id):
        resp = requests.get(f'{base}/flows/{org}/{flow}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.json())
        msg = resp.json()
        return msg

    def delete(msg_id):
        resp = requests.delete(f'{base}/flows/{org}/{flow}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200 and not resp.json(), (resp.status_code, resp.json())

    def edit(msg_id, content=None, tags=None, override_tags=False):
        """
        - at least edit `content` or `tags`
        - seems like hash tags only allow [0-9a-z_]
        - not allow modify starts with ":" tags
        - not allow override existing tags unless `overrride_tags` is True
        - by default, `override_tags` is False, and new tags will be appended to origin tags
        """
        if content is None and tags is None:
            raise TypeError('at least edit `content` or `tags`')

        payload = {}
        if content is not None:
            payload['content'] = content
        if tags is not None:
            _tags = show(msg_id)['tags']
            if override_tags:
                _tags = [t for t in _tags if re.match(r'\W', t)]
            payload['tags'] = _tags + tags

        resp = requests.put(f'{base}/flows/{org}/{flow}/messages/{msg_id}', auth=auth, json=payload)
        assert resp.status_code == 200 and not resp.json(), (resp.status_code, resp.json())

    def list(**conditions):
        resp = requests.get(f'{base}/flows/{org}/{flow}/messages', auth=auth, json=conditions)
        assert resp.status_code == 200, (resp.status_code, resp.json())
        msgs = resp.json()
        return msgs

    def events():
        stream_base = 'https://stream.flowdock.com'
        with requests.get(f'{stream_base}/flows/{org}/{flow}', auth=auth,
                          headers={'Accept':'text/event-stream'}, stream=True) as resp:
            assert resp.status_code == 200, (resp.status_code, resp.json())
            for line in resp.iter_lines():
                if line.startswith(b'data:'):
                    data = json.loads(line.decode().strip('data:').strip())
                    yield Event(data)

    return Flow(*map(locals().__getitem__, Flow._fields))


def client(token, org:str, user:Union[str, int]=None, flow:str=None):
    """
    client: token -> org -> user -> PrivateConversation
    client: token -> org -> flow -> Flow
    """
    base = 'https://api.flowdock.com'
    auth = (token, '')

    def get_uid(user_name):
        resp = requests.get(f'{base}/organizations/{org}/users', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.json())
        filtered = [u for u in resp.json() if u['nick'] == user_name]
        assert len(filtered) == 1
        return filtered[0]['id']

    if user is None and flow is None:
        c = lambda *a, **kw: client(token, org, *a, **kw)
        c.get_uid = get_uid
        return c
    elif user:
        uid = get_uid(user) if isinstance(user, str) else user
        return _private_conversation(auth, base, uid)
    elif flow:
        return _flow(auth, base, org, flow)
    else:
        raise TypeError
