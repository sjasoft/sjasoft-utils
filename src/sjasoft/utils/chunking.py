import time

# many aws functions deliver in chunks with some result indicator of more. next two functions
# are for specifying the key to provide the next indicator with and what the next_indicator
# field is
def symmetric_next(next_name):
    return (next_name, lambda r: r.get(next_name))


def asymmetric_next(next_name, next_indicator_name):
    return (next_name, lambda r: r.get(next_indicator_name))


def get_all(fn, next_chunk_extractor, data_field, **kwargs):
    '''
    Return a generator over all items returned by given function where the function
    may return items in chunks with some next indicator for more data available.
    :param fn: the function to execute repeatedly until no more data
    :param next_churk_extractor: 2-tuple of key for indicating to the function to return next chunk and
      function for getting next chunk value from current chunk
    :param data_field: key in chunk of the payload items return by fun
    :param kwargs: arguments to the function that are repeated per invocation
    :return generator over all items returned by fn
    '''
    next_key, next_val_fn = next_chunk_extractor
    res = fn(**kwargs)
    while True:
        items = res.get(data_field, [])
        for item in items:
            yield item
        next_val = next_val_fn(res)
        if next_val:
            res = fn(**kwargs, **{next_key: next_val})
        else:
            break

def fixed_sleep_wait(fn, success_test, failed_test, seconds):
    '''
    Executes a function retrieving status of something that takes some time and
    retries for fixed number of seconds returning True if success was finally indicated
    and False if failure was finally indicated.  Really just another way of doing a
    promise style pattern but more synchronously.
    :param fn: status checking function to run
    :param success_test: fn to tests for success from status checking function
    :param failed_test: fn to tests for failure from status checking function
    :param seconds: how many seconds to wait before checking again
    :return True,None if success, False,response if failure.

    NOTE: will hang forever if neither success_test or failed_test is ever satisfied or fn hangs.
    '''
    while True:
        res = fn()
        if success_test(res):
            return True, None
        if failed_test(res):
            return False, res
        time.sleep(seconds)


