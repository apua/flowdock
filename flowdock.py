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

        connect(flow_token='...', org='...', flow='...')
    """
    if kw.keys() == {'token'} or kw.keys() == {'token', 'org'}:
        # partial function
        return lambda **kwargs: connect(**kw, **kwargs)
    elif kw.keys() == {'token', 'org', 'flow'}:
        return flow(**kw)
    elif kw.keys() == {'token', 'user'} or kw.keys() == {'token', 'org', 'user'}:
        return private_message(**kw)
    elif kw.keys() == {'flow_token', 'org', 'flow'}:
        return integration(**kw)
    else:
        raise TypeError
