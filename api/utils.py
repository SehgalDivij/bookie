from django.core.cache import cache


def fetch_from_cache(chat_id):
    """
    Fetch current cache for a chat identified by a chat_id.
    :return:
    """
    chat_cache = cache.get('chat_id')
    if chat_cache is not None:
        return chat_cache
    else:
        cache.set('chat_id', {}, 600)
        return {}


def update_cache(chat_id, data=None, expiry=600):
    """
    Update a chat's cache.
    :param data:
    :param chat_id:
    :return:
    """
    cache.set(chat_id, data, expiry)


def add_to_cache(chat_id, data=None):
    """
    Add new item to cache with default expiry of 10 minutes.
    :param chat_id:
    :param data:
    :param expiry:
    :return:
    """
    cache.set(chat_id, data, 600)
