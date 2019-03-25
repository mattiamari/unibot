from datetime import datetime, timedelta

kwd_delimiter = (object(),)

def cache_for(minutes=60):
    def cache(func):
        # cache = {'key': {'data': None, 'last_update': None}}
        cache = {}

        def wrapper(*args, **kwargs):
            key = make_key(args, kwargs)
            if (key not in cache
                or cache[key]['last_update'] is None
                or datetime.now() - cache[key]['last_update'] > timedelta(minutes=minutes)):

                cache[key] = {'data': func(*args, **kwargs), 'last_update': datetime.now()}
            return cache[key]['data']
        return wrapper

    return cache

def make_key(args, kwds = None):
    # This solution is taken from
    # https://github.com/python/cpython/blob/master/Lib/functools.py#L455
    key = args
    if kwds:
        key += kwd_delimiter
        for i in kwds.items():
            key += i
    return hash(key)
