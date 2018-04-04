import pickle
from django.core.cache.backends.memcached import BaseMemcachedCache


class GaeMemcachedCache(BaseMemcachedCache):
    """
    An implementation of a cache binding using google's
    app engine memcached lib (compatible with python-memcached)
    Refer following stack overflow question:
        https://stackoverflow.com/questions/24699935/setting-up-memcached-for-django-session-caching-on-app-engine
        /24785322#24785322
    if needed
    """

    def __init__(self, server, params):
        from google.appengine.api import memcache
        super(GaeMemcachedCache, self).__init__(server, params,
                                                library=memcache,
                                                value_not_found_exception=ValueError)

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers, pickleProtocol=pickle.HIGHEST_PROTOCOL)
        return self._client
