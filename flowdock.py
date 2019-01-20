def flow(token, org, flow):
    r"""
    -   not support emoji
    -   support stream API
    """
    obj = lambda: None
    return obj


def private_message(token, user, org=None):
    r"""
    -   cache user ID at module-level
    -   use `{org}` if provided
    """
    obj = lambda: None
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
