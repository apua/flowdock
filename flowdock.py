"""
It is a simple script wrapping Flowdock API.
Please refer to the online document for usage.
"""

#   ====================
#   Development Guide
#   ====================
#
#   Design
#   ===============
#
#   Since it is just a wrapper, the wrapped API names and arguments should follow Flowdock API document.
#
#   To make it reusable unlike invoking Curl,
#   things such as API tokens should be cached for further operations that user care about,
#   like send or edit a message.
#
#   Wrapped API response should keep original response not to be modified,
#   so that user can learn what Flowdock exactly does by trial and error.
#
#   To reduce unexpected response due to user typo, wrapped API should validate supported parameters;
#   in the case of integration, the parameters in the nest JSON payload of a HTTP request should be validate, too.
#
#   Implementation
#   ===============
#
#   To make it simple, consider the form::
#
#       cache(token and URI arguments).operate(parameters and values)
#
#   Since it only requires namespace, implement callable with ``SimpleNamespace``
#   and nested function to share cached values, and implement non-callable with Python syntax ``class``.
#
#   To validate supported parameters, restrict the parameter names following origin API document,
#   and verify the parameter names for ``TypeError``.
#
#   For easy to debug, use f-string to represent URI patterns,
#   and use assertion to represent origin API response including status code and response payload.
#
#   To implement Server-Sent Events, simply follow W3C document instruction.
#
#   Testing
#   ===============
#
#   All test cases are listed in README.rst and in doctest format.
#   Invoke built-in ``doctest`` module to execute test cases.
#
#   Most of all test cases are built on Flowdock services, require real API token and channels,
#   thus one might have to adjust test data for test environment.
#   At least, they can be executed repeatedly.
#
#   Publishing
#   ===============
#
#   ``README.rst`` treated as both user guide and landing page contains:
#
#   -   Releasd version, license, and so on.
#   -   Purpose, features, and usage.
#
#   ``flowdock.py`` contains source code, real package status, and development guide in comment:
#
#   -   Version number
#   -   Design, implementation, testing, and publishing
#
#   Releases on PyPI are referred to PyPA tutorial `Packaging Python Projects`_ and leveraging ``twine``.
#   Below shows how to test publishing onto TestPyPI:
#
#   .. _`packaging python projects`: https://packaging.python.org/tutorials/packaging-projects/
#
#   .. code:: sh
#
#       $ ls setup.py
#       setup.py
#       $ rm -r dist ; python setup.py sdist bdist_wheel
#       $ twine check dist/*.whl
#       $ twine upload --user=${user} --password=${password} --repository-url https://test.pypi.org/legacy/ 'dist/*'
#
#   .. WARNING:: MUST avoid version collision, which is no way to solve even deleting it on PyPI/TestPyPI.
#
#   Release process:
#
#   1.  Merge development branch to master
#   #.  Review hard-coded information in ``setup.py``
#   #.  Bump version number in ``flowdock.py``
#   #.  Upload to TestPyPI for test
#   #.  Commit with template "Bumped version to v0.0"
#   #.  Upload to PyPI
#   #.  Tag commit and push to Github

import collections
import json
import types

import requests


__version__ = '1.0'

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
        assert (resp.status_code == 200 and not resp.json()) or (resp.status_code == 204 and not resp.content),\
                (resp.status_code, resp.content)

    def upload(file_path):
        files = {'content': open(file_path,'rb')}
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
                          headers={'Accept':'text/event-stream'}, stream=True) as resp:
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
        assert (resp.status_code == 200 and not resp.json()) or (resp.status_code == 204 and not resp.content),\
                (resp.status_code, resp.content)

    def upload(file_path):
        files = {'content': open(file_path,'rb')}
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
