"""
Flowdock API Wrapper
"""  # same as project description

import collections
import json
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
    It is reasonable because adding users is infrequent and fetching data is expensive.

    .. code:: json

        {
            "id": 336968,
            "nick": "Ray_",
            "email": "ray.zhu@hpe.com",
            "avatar": "http://somewhere.public/ray.png",
            "name": "Ray Zhu",
            "website": null
        }
    """
    if not hasattr(get_uid, 'cache'):
        get_uid.cache = {}
        resp = requests.get(f'{API}/users', auth=(token, ''))
        assert resp.status_code == 200, (resp.status_code, resp.content)
        get_uid.cache.update({u['nick']: u['id'] for u in resp.json()})

    return get_uid.cache[name]


def get_events(conn):
    """
    Interprete and yield ``Event`` object according to `Server-sent events`__ .

    __ https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation
    """
    buffer = types.SimpleNamespace(event_type='', data='', last_event_id='')
    Event = collections.namedtuple('Event', 'type data last_event_id')

    def process_field(field_name, value: str):
        if field_name == 'event':
            buffer.event_type = value
        elif field_name == 'data':
            buffer.data += value
        elif field_name == 'id':
            if '\x00' not in value:
                buffer.last_event_id = value
            else:
                pass
        elif field_name == 'retry':
            raise NotImplementedError
        else:
            pass

    for line in map(bytes.decode, conn.iter_lines()):
        if not line:
            if buffer.data:
                yield Event(buffer.event_type, buffer.data, buffer.last_event_id)
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


def flow(token, org, flow):
    auth = (token, '')

    def send(content, tags=None, thread_id=None):
        payload = {'event': 'message', 'content': content, 'tags': tags, 'thread_id': thread_id}
        resp = requests.post(f'{API}/flows/{org}/{flow}/messages', auth=auth, json=payload)
        assert resp.status_code == 201, (resp.status_code, resp.content)
        return resp.json()

    def show(msg_id):
        resp = requests.get(f'{API}/flows/{org}/{flow}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.json()

    def edit(msg_id, content=None, tags=None):
        payload = {}

        if content is not None:
            payload['content'] = content

        if tags is not None:
            payload['tags'] = tags

        resp = requests.put(f'{API}/flows/{org}/{flow}/messages/{msg_id}', auth=auth, json=payload)
        assert resp.status_code == 200 and not resp.json(), (resp.status_code, resp.content)

    def delete(msg_id):
        resp = requests.delete(f'{API}/flows/{org}/{flow}/messages/{msg_id}', auth=auth)
        assert (resp.status_code == 200 and not resp.json()) or (resp.status_code == 204 and not resp.content), \
            (resp.status_code, resp.content)

    def upload(file_path):
        files = {'content': open(file_path, 'rb')}
        data = {'event': 'file'}
        resp = requests.post(f'{API}/flows/{org}/{flow}/messages', auth=auth, files=files, data=data)
        assert resp.status_code == 201, (resp.status_code, resp.content)
        return resp.json()

    def download(uri_path):
        resp = requests.get(f'{API}/{uri_path}', auth=auth)
        assert [r.status_code for r in resp.history] == [302], (uri_path, resp.history)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.content

    def list(**conditions):
        supported_parameters = ('search', 'tags', 'tag_mode', 'skip', 'limit', 'event', 'since_id', 'until_id', 'sort')
        for para in conditions.keys():
            if para not in supported_parameters:
                raise TypeError(f'got unsupported parameter \'{para}\'; '
                                f'supported parameters are: {supported_parameters}')
        resp = requests.get(f'{API}/flows/{org}/{flow}/messages', auth=auth, json=conditions)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.json()

    def threads(**conditions):
        supported_parameters = ('limit', 'since', 'until', 'application', 'empty')
        for para in conditions.keys():
            if para not in supported_parameters:
                raise TypeError(f'got unsupported parameter \'{para}\'; '
                                f'supported parameters are: {supported_parameters}')
        resp = requests.get(f'{API}/flows/{org}/{flow}/threads', auth=auth, json=conditions)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.json()

    def thread(thread_id):
        return threading(token, org, flow, thread_id)

    def events():
        with requests.get(f'{STREAM}/flows/{org}/{flow}', auth=auth,
                          headers={'Accept': 'text/event-stream'}, stream=True) as resp:
            assert resp.status_code == 200, (resp.status_code, resp.content)
            yield from (json.loads(e.data) for e in get_events(resp))

    return types.SimpleNamespace(**locals())


def threading(token, org, flow, thread_id):
    auth = (token, '')

    def send(content, tags=None):
        payload = {'event': 'message', 'content': content, 'tags': tags}
        resp = requests.post(f'{API}/flows/{org}/{flow}/threads/{thread_id}/messages', auth=auth, json=payload)
        assert resp.status_code == 201, (resp.status_code, resp.content)
        return resp.json()

    def list(**conditions):
        resp = requests.get(f'{API}/flows/{org}/{flow}/threads/{thread_id}/messages', auth=auth, json=conditions)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.json()

    return types.SimpleNamespace(**locals())


def private(token, uid):
    auth = (token, '')

    def send(content, tags=None):
        payload = {'event': 'message', 'content': content, 'tags': tags}
        resp = requests.post(f'{API}/private/{uid}/messages', auth=auth, json=payload)
        assert resp.status_code == 201, (resp.status_code, resp.content)
        return resp.json()

    def show(msg_id):
        resp = requests.get(f'{API}/private/{uid}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.json()

    def edit(msg_id, content=None, tags=None):
        payload = {}

        if content is not None:
            payload['content'] = content

        if tags is not None:
            payload['tags'] = tags

        resp = requests.put(f'{API}/private/{uid}/messages/{msg_id}', auth=auth, json=payload)
        assert resp.status_code == 200 and not resp.json(), (resp.status_code, resp.content)

    def delete(msg_id):
        resp = requests.delete(f'{API}/private/{uid}/messages/{msg_id}', auth=auth)
        assert (resp.status_code == 200 and not resp.json()) or (resp.status_code == 204 and not resp.content), \
            (resp.status_code, resp.content)

    def upload(file_path):
        files = {'content': open(file_path, 'rb')}
        data = {'event': 'file'}
        resp = requests.post(f'{API}/private/{uid}/messages', auth=auth, files=files, data=data)
        assert resp.status_code == 201, (resp.status_code, resp.content)
        return resp.json()

    def download(uri_path):
        resp = requests.get(f'{API}/{uri_path}', auth=auth)
        assert [r.status_code for r in resp.history] == [302], (uri_path, resp.history)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.content

    def list(**conditions):
        supported_parameters = ('search', 'tags', 'tag_mode', 'skip', 'limit', 'event', 'since_id', 'until_id', 'sort')
        for para in conditions.keys():
            if para not in supported_parameters:
                raise TypeError(f'got unsupported parameter \'{para}\'; '
                                f'supported parameters are: {supported_parameters}')
        resp = requests.get(f'{API}/private/{uid}/messages', auth=auth, json=conditions)
        assert resp.status_code == 200, (resp.status_code, resp.content)
        return resp.json()

    return types.SimpleNamespace(**locals())


def integration(flow_token):
    def present(id, author, title, body=None, thread=None):
        payload = {'flow_token': flow_token, 'external_thread_id': id, 'author': author, 'title': title}

        if body is None:
            payload['event'] = 'activity'
        else:
            payload['event'] = 'discussion'
            payload['body'] = body

        if thread is not None:
            payload['thread'] = thread

        resp = requests.post(f'{API}/messages', json=payload)
        assert resp.status_code == 202 and not resp.json(), (resp.status_code, resp.content)

    return types.SimpleNamespace(**locals())


class constructors:
    def __new__(*a, **kw):
        raise TypeError('it is not callable')

    def author(name, avatar=None):
        return locals()

    def thread(title, body=None, fields=None, status=None, external_url=None, actions=None):
        return locals()

    def field(label, value):
        return locals()

    def status(color, value):
        supported_colors = ('black', 'blue', 'cyan', 'green', 'grey', 'lime', 'orange', 'purple', 'red', 'yellow')
        if color not in supported_colors:
            raise TypeError(f'got invalid color; supported colors are: {supported_colors}')
        return {'color': color, 'value': value}


def connect(**kw):
    """
    Connect Flowdock to initialize a client to join a flow or private channel.

    It supports multiple usage for different cases.

    Switch among flow/private channels::

        client = flowdock.connect(token=PERSONAL_API_TOKEN)
        flow = client(org=ORG_NAME, flow=FLOW_NAME)
        private = client(uid=USER_ID)

    Join a channel in one line::

        flow = flowdock.connect(token=PERSONAL_API_TOKEN, org=ORG_NAME, flow=FLOW_NAME)
        private = flowdock.connect(token=PERSONAL_API_TOKEN, uid=USER_ID)
        private = flowdock.connect(token=PERSONAL_API_TOKEN, name=USER_NAME)

    Connect by integrate external services::

        external_service = flowdock.connect(flow_token=FLOW_TOKEN)
    """
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
        raise TypeError('got at least one unexpected keyword argument; refer to document for the usage')
