import collections
import re
import types

import requests

API = 'https://api.flowdock.com'
STREAM = 'https://stream.flowdock.com'


def get_uid(token, name) -> int:
    """
    Get UID by display name.

    The dumped user data is formed as below.
    Note that ``nick`` (i.e. "Display name" field in "Edit profile" page) is unique,
    but ``name`` (i.e "Name" field in "Edit profile" page) is not.

    Therefore, it is nothing different between searching with organization/flow or not.

    This function also cache user ``nick - id`` mapping.
    It is reasonable because of less adding users and expensive fetching data.

    .. code:: json

        {
            "id": 336968,
            "nick": "Ray_",
            "email": "ray.zhu@hpe.com",
            "avatar": "https://d2cxspbh1aoie1.cloudfront.net/avatars/local/4965d1f57b777771d2baf1a71dccaa9a61d0c6050d9b37d5e58380cdff56d813/",
            "name": "Ray Zhu",
            "website": null
        }
    """
    if not hasattr(get_uid, 'cache'):
        get_uid.cache = {}
        resp = requests.get(f'{API}/users', auth=(token, ''))
        assert resp.status_code == 200, (resp.status_code, resp.json())
        get_uid.cache.update({u['nick']: u['id'] for u in resp.json()})

    return get_uid.cache[name]


def get_events(conn):
    """
     Interprete and yield ``Event`` object according to `Server-sent events`__ .

    __ https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation
    """
    buffer = types.SimpleNamespace(event_type='', data='', last_event_id='')

    def process_field(field_name, value: str):
        if field_name == 'event':
            buffer.event_type = value
        elif field_name == 'data':
            buffer.data += value
        elif field_name == 'id':
            if '\x00' not in value:
                buffer.last_event_id = value
        elif field_name == 'retry':
            raise NotImplementedError('cannot set reconnection time')
        else:
            pass

    for line in map(bytes.decode, conn.iter_lines()):
        if not line:
            if buffer.data:
                yield get_events.Event(buffer.event_type, buffer.data, buffer.last_event_id)
            buffer.event_type = buffer.data = ''
        elif line.startswith(':'):
            pass
        elif ':' in line:
            field_name, tail = line.split(':', 1)
            value = tail.lstrip(' ')
            process_field(field_name, value)
        else:
            field_name = line
            process_field(field_name, '')

get_events.Event = collections.namedtuple('Event', 'type data last_event_id')


# `flow` is not support emoji ?

def flow(token, org, flow):
    auth = (token, '')

    def send(content, tags=None):
        json = {'event': 'message', 'content': content, 'tags': tags}
        resp = requests.post(f'{API}/flows/{org}/{flow}/messages', auth=auth, json=json)
        assert resp.status_code == 201, (resp.status_code, resp.content)
        return resp.json()['id']

    def show(msg_id):
        resp = requests.get(f'{API}/flows/{org}/{flow}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.json()

    def edit(msg_id, content=None, tags=None, override_tags=False):
        """
        -   at least edit `content` or `tags`
        -   not allow modify starts with ':' tags
        -   not allow override existing tags unless `overrride_tags` is True
        -   by default, `override_tags` is False, and new tags will be appended to origin tags
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

        resp = requests.put(f'{API}/flows/{org}/{flow}/messages/{msg_id}', auth=auth, json=payload)
        assert resp.status_code == 200 and not resp.json(), (resp.status_code, resp.content)

    def delete(msg_id):
        resp = requests.delete(f'{API}/flows/{org}/{flow}/messages/{msg_id}', auth=auth)
        assert (resp.status_code == 200 and not resp.json()) or (resp.status_code == 204 and not resp.content),\
                (resp.status_code, resp.content)

    def upload(file_path):
        files = {'content': open(file_path,'rb')}
        data = {'event': 'file'}
        resp = requests.post(f'{API}/flows/{org}/{flow}/messages', auth=auth, files=files, data=data)
        assert resp.status_code == 201, (resp.status_code, resp.content)
        return resp.json()['id']

    def download(uri_path):
        resp = requests.get(f'{API}/{uri_path}', auth=auth)
        assert [r.status_code for r in resp.history] == [302], (uri_path, resp.history)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.content

    def list(**conditions):
        resp = requests.get(f'{API}/flows/{org}/{flow}/messages', auth=auth, json=conditions)
        assert resp.status_code == 200, (resp.status_code, resp.json())
        return resp.json()

    def events():
        with requests.get(f'{STREAM}/flows/{org}/{flow}', auth=auth,
                          headers={'Accept':'text/event-stream'}, stream=True) as resp:
            assert resp.status_code == 200, (resp.status_code, resp.json())
            yield from get_events(resp)
            # TODO: parse the output of `get_events` for easy usage
            # TODO: support `EventSource` interface, hook callbacks, which is easier to use

    return types.SimpleNamespace(**locals())


def private(token, uid):
    auth = (token, '')

    def send(content):
        resp = requests.post(f'{API}/private/{uid}/messages', auth=auth, json={'event':'message','content':content})
        assert resp.status_code == 201, (resp.status_code, resp.content)
        return resp.json()['id']

    def show(msg_id):
        resp = requests.get(f'{API}/private/{uid}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.json()

    def edit(msg_id, content):
        resp = requests.put(f'{API}/private/{uid}/messages/{msg_id}', auth=auth, json={'content':content})
        assert resp.status_code == 200 and not resp.json(), (resp.status_code, resp.content)

    def delete(msg_id):
        resp = requests.delete(f'{API}/private/{uid}/messages/{msg_id}', auth=auth)
        assert (resp.status_code == 200 and not resp.json()) or (resp.status_code == 204 and not resp.content),\
                (resp.status_code, resp.content)

    def upload(file_path):
        files = {'content': open(file_path,'rb')}
        data = {'event': 'file'}
        resp = requests.post(f'{API}/private/{uid}/messages', auth=auth, files=files, data=data)
        assert resp.status_code == 201, (resp.status_code, resp.content)
        return resp.json()['id']

    def download(uri_path):
        resp = requests.get(f'{API}/{uri_path}', auth=auth)
        assert [r.status_code for r in resp.history] == [302], (uri_path, resp.history)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.content

    def list(**conditions):
        resp = requests.get(f'{API}/private/{uid}/messages', auth=auth, json=conditions)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.json()

    return types.SimpleNamespace(**locals())


def integration(flow_token):
    r"""
    -   use `{org}/{flow}` if provided
    -   support partial function
    """
    return types.SimpleNamespace(**locals())


def connect(**kw):
    if kw.keys() == {'token'}:
        partial = lambda **kwargs: connect(**kw, **kwargs)
        partial.get_uid = lambda **kwargs: get_uid(**kw, **kwargs)
        return partial
    elif kw.keys() == {'token', 'org', 'flow'}:
        return flow(**kw)
    elif kw.keys() == {'token', 'uid'}:
        return private(**kw)
    elif kw.keys() == {'token', 'name'}:
        return private(token=kw['token'], uid=get_uid(**kw))
    elif kw.keys() == {'flow_token'}:
        return integration(**kw)
    else:
        raise TypeError
