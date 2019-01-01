Present integrated external service
-----------------------------------

.. code:: python

    >>> from token import FLOW_TOKEN
    >>> myflow = flowdock.client(flow_token=FLOW_TOKEN, org='hpe', flow='apua-bot-1')

    # still in design ...
    >>> #thread = myflow.get(external_thread_id='oooooooooo')
    >>> #thread = myflow.find(thread_title='xxx')
    >>> all_activities = myflow.list(event='activity')

    >>> thread = myflow.present(external_thread_id:id, thread:dict)
    >>> thread.post(author:'Ray_', title:'created', avatar:'http://...' | None)
    >>> thread.post(author:'Apua', title:'updated', avatar:'http://...' | None)

.. code:: python

    class Item:
        external_url
        status
        title
        body
        fields
        post: author -> message -> IO None

    # not finished yet
    def item(flow_token, external_id, thread):
        def post(author, avatar=None):
            payload = {'thread':thread,'author':author,'avatar':avatar}
            resp = requests.post(f'{base}/flows/{org}/{flow}/messages', auth, json=payload)

    def present(flow_token, **thread):
        support_status_colors = ('blue', 'red', 'green', 'yellow', 'cyan', 'orange', 'grey', 'black', 'lime', 'purple')
        if not thread:
            return lambda **thread: present(flow_token, **thread)
        else:
            if any(k not in ('external_id', 'title', 'fields', 'body', 'status', 'external_url') for k in thread):
                raise TypeError('allow attributes: `fields`, `body`, `status`, `external_url`')
            if 'external_id' not in thread or 'title' not in thread:
                raise TypeError('`external_id` and `title` are required')
            if 'fields' in thread:
                if not isinstance(thread['fields'], dict):
                    raise ValueError('`fields` should be key-value pair')
            if 'status' in thread:
                if not isinstance(thread['status'], (list, tuple)):
                    raise ValueError('`status` must be 2 pair in list / tuple')
                if thread['status'][0] not in support_status_colors:
                    raise ValueError(f'`status` color supports: {support_status_colors}')
            if 'external_url' in thread:
                if not re.match('^https?://', thread['external_url']):
                    raise ValueError(f'`external_url` requires valid URI')

            external_id = thread['external_id']
            thread.setdef
            del thread['external_id']
            return item(flow_token, thread['external_id'], thread)
