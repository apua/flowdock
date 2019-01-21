import requests

API = 'https://api.flowdock.com'
STREAM = 'https://stream.flowdock.com'


def get_uid(auth, user, org=None):
    if isinstance(user, int):
        uid = user
    elif user in get_uid.users:
        uid = get_uid.users[user]
    else:
        resp = requests.get(f'{API}/users' if org is None else f'{API}/organizations/{org}/users', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.json())
        get_uid.users.update({u['nick']: u['id'] for u in resp.json()})
        uid = get_uid.users[user]

    return uid
get_uid.users = {}


def flow(token, org, flow):
    r"""
    -   not support emoji
    -   support stream API

    >>> from tests.tokens import PERSONAL_API_TOKEN
    >>> myflow = flow(PERSONAL_API_TOKEN, 'hpe', 'apua-flow')
    >>> msg_id = myflow.send('doctest')
    >>> myflow.show(msg_id)
    """
    auth = (token, '')

    def send(content, tags=None):
        json = {'event': 'message', 'content': content, 'tags': tags}
        resp = requests.post(f'{API}/flows/{org}/{flow}/messages', auth=auth, json=json)
        assert resp.status_code == 201, (resp.status_code, resp.json())
        return resp.json()['id']

    def show(msg_id):
        resp = requests.get(f'{API}/flows/{org}/{flow}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.json())
        return resp.json()

    obj = lambda: None
    obj.__dict__.update(locals())
    return obj


def private_message(token, user, org=None):
    r"""
    -   cache user ID at module-level
    -   use `{org}` if provided

    >>> from tests.tokens import PERSONAL_API_TOKEN
    >>> ray = private_message(PERSONAL_API_TOKEN, 'Ray_')
    >>> msg_id = ray.send('doctest')
    >>> ray.show(msg_id)
    """
    auth = (token, '')
    uid = get_uid(auth, user, org)

    def send(content):
        resp = requests.post(f'{API}/private/{uid}/messages', auth=auth, json={'event':'message','content':content})
        assert resp.status_code == 201, (resp.status_code, resp.json())
        return resp.json()['id']

    def show(msg_id):
        resp = requests.get(f'{API}/private/{uid}/messages/{msg_id}', auth=auth)
        assert resp.status_code == 200, (resp.status_code, resp.json())
        return resp.json()

    obj = lambda: None
    obj.__dict__.update(locals())
    return obj


def integration(flow_token, org=None, flow=None):
    r"""
    -   use `{org}/{flow}` if provided
    -   support partial function
    """
    if org is None and flow is None:
        obj = lambda org, flow: integration(flow_token, org, flow)
        "less support"
    elif org is not None and flow is not None:
        obj = lambda: None
        "more support"
    else:
        raise TypeError
    return obj


def connect(**kw):
    r"""
    To connect flow::

        connect(token='...', org='...', flow='...')
        connect(token='...')(org='...', flow='...')

    To connect private message::

        connect(token='...', user='...')
        connect(token='...')(user='...')
        connect(token='...', org='...')(user='...')
        connect(token='...', org='...', user='...')

    To connect integration::

        connect(flow_token='...')
        connect(flow_token='...', org='...', flow='...')
    """
    if kw.keys() == {'token'} or kw.keys() == {'token', 'org'}:
        # partial function
        return lambda **kwargs: connect(**kw, **kwargs)
    elif kw.keys() == {'token', 'org', 'flow'}:
        return flow(**kw)
    elif kw.keys() == {'token', 'user'} or kw.keys() == {'token', 'org', 'user'}:
        return private_message(**kw)
    elif kw.keys() == {'flow_token'} or kw.keys() == {'flow_token', 'org', 'flow'}:
        return integration(**kw)
    else:
        raise TypeError
