# -*- coding: utf-8 -*-

"""
requests.async
~~~~~~~~~~~~~~

This module contains an asynchronous replica of ``requests.api``, powered
by gevent or eventlet. All API methods return a ``Request`` instance (as opposed to
``Response``). A list of requests can be sent with ``map()``.
"""

from .config import settings

if settings.async_module not in ('gevent', 'eventlet'):
    raise RuntimeError('async_module can only be one of "gevent" or "eventlet"')

async_module = None
if settings.async_module == "gevent":
    try:
        import gevent
        from gevent import monkey as curious_george
        async_module = 'gevent'
    except ImportError:
        pass

if async_module is None:
    try:
        import eventlet
        from eventlet import patcher as curious_george
        curious_george.patch_all = curious_george.monkey_patch
        async_module = 'eventlet'
    except ImportError:
        raise RuntimeError('Gevent or Eventlet is required for requests.async.')

# Monkey-patch.
curious_george.patch_all(thread=False)

from . import api
from .hooks import dispatch_hook


__all__ = (
    'map',
    'get', 'head', 'post', 'put', 'patch', 'delete', 'request'
)


def _patched(f):
    """Patches a given API function to not send."""

    def wrapped(*args, **kwargs):
        return f(*args, return_response=False, **kwargs)

    return wrapped


def _send(r, pools=None):
    """Sends a given Request object."""

    if pools:
        r._pools = pools

    r.send()

    # Post-request hook.
    r = dispatch_hook('post_request', r.hooks, r)

    # Response manipulation hook.
    r.response = dispatch_hook('response', r.hooks, r.response)

    return r.response


# Patched requests.api functions.
get = _patched(api.get)
head = _patched(api.head)
post = _patched(api.post)
put = _patched(api.put)
patch = _patched(api.patch)
delete = _patched(api.delete)
request = _patched(api.request)


def map(requests, prefetch=True):
    """Concurrently converts a list of Requests to Responses.

    :param requests: a collection of Request objects.
    :param prefetch: If False, the content will not be downloaded immediately.
    """

    if async_module == 'gevent':
        jobs = [gevent.spawn(_send, r) for r in requests]
        gevent.joinall(jobs)
    else:
        pool = eventlet.GreenPool()
        [pool.spawn(_send, r) for r in requests]
        pool.waitall()

    if prefetch:
        [r.response.content for r in requests]

    return [r.response for r in requests]




