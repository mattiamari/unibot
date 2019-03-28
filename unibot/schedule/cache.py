from datetime import datetime, timedelta

def cache_for(minutes=60):
    def cache(func):
        # cache = {'key': {'data': None, 'last_update': None}}
        cache = {}
        duration = timedelta(minutes=minutes)

        def wrapper(*args, **kwargs):
            key = make_key(args, kwargs)
            now = datetime.now()
            if (key not in cache
                or cache[key]['last_update'] is None
                or now - cache[key]['last_update'] > duration):

                cache[key] = {'data': func(*args, **kwargs), 'last_update': now}
            return cache[key]['data']
        return wrapper

    return cache

kwd_delimiter = (object(),)

def make_key(args, kwds = None):
    # This solution is taken from
    # https://github.com/python/cpython/blob/master/Lib/functools.py#L455
    key = args
    if kwds:
        key += kwd_delimiter
        for i in kwds.items():
            key += i
    return hash(key)
