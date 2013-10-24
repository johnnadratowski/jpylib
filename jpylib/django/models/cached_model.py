"""
Contains the cached model
"""
import types

from django.core.cache import cache

from .base import BaseModel


class CachedModel(BaseModel):
    """
    Class that adds caching functionality to an object.  Allows cache invalidation
    through the save() and delete() methods.  Has a built-in cache key for the class
    as well.
    """

    MODEL_CACHE_KEY = 'model-cache-%s-%s'
    MODEL_ATTR_LIST_CACHE_KEY = 'model-cache-%s-%s-attrs-list'
    MODEL_ATTR_CACHE_KEY = 'model-cache-attr-%s-%s-%s'
    FILTER_CACHE_KEY = 'filter-cache-%s-%s'
    FILTER_ITEM_LIST_CACHE_KEY = 'filter-cache-%s-%s-list'
    # Set default timeout to max - 30 days. Invalidation should occur on save anyway.
    # Can be overridden by derived class
    MODEL_CACHE_TIMEOUT = 60 * 60 * 24 * 30

    @classmethod
    def cache_filter(cls, filter_args, timeout=MODEL_CACHE_TIMEOUT):
        """
        Gets a queryset of objects of this type, and caches the queryset

        :param cls: The class that this call is made for
        :type cls: class
        :param filter_args: The filter to use to get the queryset
        :type filter_args: dict (kwargs)
        :param timeout: The length of time (in seconds) to cache the queryset
        :type timeout: int
        :returns: The queryset of cached objects

        THIS WILL EVALUATE THE QUERYSET EVERY TIME!
        """

        key = cls._get_filter_cache_key(filter_args)
        queryset = cache.get(key)
        if not queryset:
            queryset = cls.objects.filter(**filter_args)
            cache.set(key, queryset, timeout)

            cls.store_filter_item_list(key, queryset, timeout)

        return queryset

    @classmethod
    def store_filter_item_list(cls, key, queryset, timeout=MODEL_CACHE_TIMEOUT):
        """
        When caching a queryset, this will cache a list of the querysets each item is cached
        in, so that those querysets can be invalidated when the object is updated

        :param key: The key of the queryset cache
        :type key: string
        :param queryset: The queryset that was cached
        :type queryset: Queryset
        :param timeout: The length in seconds to store the filter item list cache
        :type timeout: int
        """

        # Keep a list of items in the queryset that are cached, so if these items
        # are updated later, we can invalidate this queryset cache

        for item in queryset:
            item_key = cls._get_filter_item_list_cache_key(item.id)
            filter_list = cache.get(item_key)
            if not filter_list:
                filter_list = []

            filter_list.append(key)
            cache.set(item_key, filter_list, timeout)

    @classmethod
    def _invalidate_filter_cache_for_item(cls, id):
        """
        Invalidates all of the cached querysets that the item with the given ID is stored in

        :param id: The id of the object we're invalidating querysets for
        :type id: string or int
        """

        # get the list of cache keys for cached querysets the item with the given id belongs to
        key = cls._get_filter_item_list_cache_key(id)
        to_invalidate = cache.get(key)

        if to_invalidate:
            # invalidate each cached queryset for the given item ID
            for filter_key in to_invalidate:
                cache.delete(filter_key)

        cache.delete(key)

    @classmethod
    def cache_get(cls, id, timeout=MODEL_CACHE_TIMEOUT):
        """
        Gets an item from the cache if it exists.  If it doesn't exist, queries for the item
        and then saves it in the cache

        :param cls: The class that this call is made for
        :type cls: class
        :param id: The id of the object we're getting
        :type id: int
        :param timeout: The length of time (in seconds) to cache the model
        :type timeout: int
        :returns: The item with the given id for this class
        """
        key = cls._get_cache_key(id)
        obj = cache.get(key)

        if not obj:
            obj = cls.objects.get(id=id)
            cache.set(key, obj, timeout)

        return obj

    @classmethod
    def _get_filter_item_list_cache_key(cls, id):
        """
        Gets the cache key for the filter item list.
        The filter item list is used to determine which items
        are in which cached querysets, so those cached querysets
        can be invalidated when that item is changed.

        RETURNS:
            The cache key for the filter item list

        PARAMS:
            cls(class):
                The class of the object were getting the filter item list cache key for
            id(id (string or int)):
                The id of the object we're getting the filter item list cache key for
        """
        return CachedModel.FILTER_ITEM_LIST_CACHE_KEY % (cls.__name__, id)

    @classmethod
    def _get_filter_cache_key(cls, filter):
        """
        Gets the cache key for the filter.  This is used for caching querysets

        RETURNS:
            The cache key for the filter

        PARAMS:
            cls(class):
                The class of the object were getting the filter item list cache key for
            filter(dict):
                The filter that was used to obtain the queryset
        """
        key = ','.join(["%s:%s" % (k,v) for k,v in filter.iteritems()])
        return CachedModel.FILTER_CACHE_KEY % (cls.__name__, key)

    @classmethod
    def _get_cache_key(cls, id):
        """
        Gets the cache key for the item.

        RETURNS:
            The cache key for the item

        PARAMS:
            cls(class):
                The class of the object were getting the cache key for
            id(id (string or int)):
                The id of the object we're getting the cache key for
        """
        return CachedModel.MODEL_CACHE_KEY % (cls.__name__, id)

    @classmethod
    def _invalidate_cached_attrs(cls, id):
        """
        Invalidates the cache for all cached attributes of an instance

        RETURNS:
            Void

        PARAMS:
            cls(class):
                The class of the object were invalidating all cached attrs for
            id(id (string or int)):
                The id of the object we're invalidating all cached attrs for
        """
        # Get the cache key of the list of cached attributes
        cached_attrs_key = cls._get_attr_list_cache_key(id)

        # Get the list of cached attributes cache keys form teh cache
        cached_attr_keys = cache.get(cached_attrs_key)

        # Invalidate all cached attributes
        if cached_attr_keys:
            for attr_key in cached_attr_keys:
                cache.delete(attr_key)

        # Invalidate the list of attributes cache keys
        cache.delete(cached_attrs_key)

    @classmethod
    def _get_attr_list_cache_key(cls, id):
        """
        Gets the cache key for the list of cached attributes for the item.

        RETURNS:
            The cache key for the items list of cached attributes

        PARAMS:
            cls(class):
                The class of the object were getting the cache key for
            id(id (string or int)):
                The id of the object we're getting the cache key for
        """
        return CachedModel.MODEL_ATTR_LIST_CACHE_KEY % (cls.__name__, id)

    @classmethod
    def _get_attr_cache_key(cls, id, attr):
        """
        Gets the cache key for a cached attribute for the model instance.

        RETURNS:
            The cache key for the items cached attribute

        PARAMS:
            cls(class):
                The class of the object were getting the cache key for
            id(id (string or int)):
                The id of the object we're getting the cache key for
            attr(string):
                The attribute we're getting the cache key for
        """
        return CachedModel.MODEL_ATTR_CACHE_KEY % (cls.__name__, id, attr)

    @classmethod
    def cache_remove_multiple(cls, ids):
        """
        Removes a list of ids from the cache

        RETURNS:
            Void

        PARAMS:
            cls(class):
                The class of the object were removing items from the cache for
            ids(list of ids or objects):
                The ids we're removing from the cache
        """
        for id in ids:
            # Allows for instances to be passed in teh list
            if isinstance(id, cls):
                id.cache_remove()
            else:
                cls.cache_remove_id(id)

    @classmethod
    def cache_remove_id(cls, id):
        """
        Removes the object with the given id from the cache

        RETURNS:
            Void

        PARAMS:
            cls(class):
                The class of the object removing from the cache
            id(id (string or int)):
                The id of the object we're removing from the cache
        """
        cache.delete(cls._get_cache_key(id))

    def cache_remove(self):
        """ Removes this object instance from the cache """
        self.cache_remove_id(self.id)

    def get_cache_key(self):
        """ Gets the cache key for this object instance """
        return self._get_cache_key(self.id)

    def cache_get_attr(self, attr, timeout=MODEL_CACHE_TIMEOUT):
        """
        Gets and caches an attribute for this model instance.
        Useful for caching foreign key relationships

        RETURNS:
            The attribute that is being retrieved

        PARAMS:
            attr(string):
                Period-delimited string of attributes to get. Using the
                dot delimiter will traverse attribute child attributes
        """
        # Get the key for the cached attribute and the list of cached attributes
        list_key = self._get_attr_list_cache_key(self.id)
        attr_key = self._get_attr_cache_key(self.id, attr)

        # Traverse the attributes and get the attribute the user is requesting
        cur_attr = self
        for attr_name in attr.split('.'):
            cur_attr = getattr(cur_attr, attr_name)

            # If this is a method, we call the method.
            # Will only work with methods with no required args
            if isinstance(cur_attr, types.FunctionType) or isinstance(cur_attr, types.MethodType):
                cur_attr = cur_attr()

        # Add attribute to the cache
        cache.set(attr_key, cur_attr, timeout)

        # Add the key of the attribute cache to the list of attribute caches
        cache_attr_list = cache.get(list_key)
        if not cache_attr_list:
            cache_attr_list = []
        cache_attr_list.append(attr_key)

        cache.set(list_key, cache_attr_list, timeout)

        return cur_attr

    def invalidate_caches(self):
        """ Invalidates all caches for this cache model instance.  All cached querysets,
        all cached attributes, and the cache for this object itself will be invalidated"""

        self._invalidate_filter_cache_for_item(self.id)

        self._invalidate_cached_attrs(self.id)

        self.cache_remove()

    def save(self, timeout=MODEL_CACHE_TIMEOUT, *args, **kwargs):
        """
        Overrides default model save method to re-cache the updated objects information

        RETURNS:
            Void

        PARAMS:
            timeout(int):The length in secodns to store the object in the cache
        """
        is_insert = self.id is None or kwargs.get('force_insert', False)

        super(CachedModel, self).save(*args, **kwargs)

        if not is_insert:
            # Invalidate all caches for this model on save, only if this is not getting inserted
            self.invalidate_caches()

        # Update cache with saved item
        cache.set(self.get_cache_key(), self, timeout)

    def delete(self, *args, **kwargs):
        """
        Overrides default model delete method to remove a deleted item from the cache
        """
        super(CachedModel, self).delete(*args, **kwargs)

        self.invalidate_caches()

    class Meta:
        abstract = True


