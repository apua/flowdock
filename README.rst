====================
Flowdock API wrapper
====================

:Official API Document: https://www.flowdock.com/api
:Official API Document Repository: https://github.com/flowdock/api-docs

The origin Flowdock API document is outdate.
This tool aim to be an intuitive wrapper summarizes the usage.


Usage
====================

.. contents:: Tabe of Contents
    :local:


Authentication and Channel
------------------------------

.. private channel (limit support)
.. flow
.. quick switch flow and private


Message
------------------------------

.. send, get, edit, delete


File
------------------------------

.. upload, download


Tag
------------------------------

.. send, edit


Thread
------------------------------

.. reply (get thread id)  # `external_thread_id` ?


Present External Item
------------------------------

.. update item states w/wo item detail as a thread
.. describe item detail
.. reply onto item (both user and bot)


Monitor Flow
------------------------------


List
------------------------------


.. text search and tagged -- search x tags x tags_mode x skip x limit
.. file and activitie -- event x sort x since_id x until_id x limit
.. list threads and list messages in given thread
.. link and email


Get UID by Display Name
------------------------------

.. >>> client.get_uid('Ray_')
.. 336968
.. >>> ray = client(336968)
