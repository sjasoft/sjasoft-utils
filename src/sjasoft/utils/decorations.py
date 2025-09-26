import random
import asyncio
from functools import wraps

def synchronized(func):
    @wraps(func)
    def _guarded(*args, **kwargs):
        lock = args[0]._instance_lock
        with lock:
            return func(*args, **kwargs)
    return _guarded

def abstract(func):
    @wraps(func)
    def inner(*args, **kwargs):
      raise Exception('%s needs a non-abstract implementation' % func.__name__)
    return inner



def async_wrapper(coro):
    '''
    This decorator allows an asynchronous function wrapped with it to execute synchronously by waiting for
    the event loop to finish with it.  It should be used sparingly and generally only where we are at a logical
    top of a single rooted hierarchy or within a framework that expects non-async functions or methods.
    :param coro: the async or coroutien function being wrapped
    :return: the result of the waited for wrapped function.
    '''

    @wraps(coro)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))

    return wrapper
