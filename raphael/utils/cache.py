# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function
import abc
from memcache import Client
from raphael.utils import strings, setting, objects
from raphael.utils.dao.context import DBContext

memcached_setting = setting.conf['cache']['memcached']
memcached_server_list = memcached_setting['server_list'] if memcached_setting.get('enabled') else []
memcached_client = Client(memcached_server_list)
PRIMARY_IDENTIFIER = 'id'


class AbstractMemcached(objects.Singleton):
    prefix = ''
    with_flush = False

    @classmethod
    @abc.abstractclassmethod
    def actual_save(cls, key, obj):
        pass

    @classmethod
    @abc.abstractclassmethod
    def actual_remove(cls, key):
        pass

    @classmethod
    @abc.abstractclassmethod
    def actual_get(cls, key):
        pass

    @classmethod
    def _flush_uniq(cls):
        uniq = strings.uuid()
        memcached_client.set('~' + cls.prefix, uniq)
        return uniq

    @classmethod
    def _get_exact_key(cls, key):
        uniq = ''
        if cls.with_flush:
            uniq = memcached_client.get('~' + cls.prefix)
            if not uniq:
                uniq = cls._flush_uniq()
        return ':'.join((cls.prefix, uniq, key))

    @classmethod
    def _get_cache(cls, key):
        return memcached_client.get(cls._get_exact_key(key))

    @classmethod
    def _save_cache(cls, key, obj, time=0):
        if strings.is_not_blank(key):
            return memcached_client.set(cls._get_exact_key(key), obj, time=time)
        return None

    @classmethod
    def _remove_cache(cls, key):
        return memcached_client.delete(cls._get_exact_key(key))

    @classmethod
    def save(cls, key, obj, time=0):
        cls.actual_save(key, obj)
        cls._save_cache(key, obj, time=time)

    @classmethod
    def remove(cls, key):
        cls._remove_cache(key)
        cls.actual_remove(key)

    @classmethod
    def get(cls, key):
        if key is None:
            return None
        obj = cls._get_cache(key)
        if obj is not None:
            return obj
        else:
            obj = cls.actual_get(key)
            cls._save_cache(key, obj)
            return obj

    @classmethod
    def flush_all(cls):
        if cls.with_flush:
            cls._flush_uniq()


class DBMemcached(AbstractMemcached):
    index_key = PRIMARY_IDENTIFIER

    @classmethod
    def actual_remove(cls, key):
        DBContext().execute_delete(cls.prefix, cls.index_key + '=:indexkey', indexkey=key)

    @classmethod
    def actual_save(cls, key, obj):
        DBContext().save(cls.prefix, obj)

    @classmethod
    def actual_get(cls, key):
        if cls.index_key == PRIMARY_IDENTIFIER:
            return DBContext().get(cls.prefix, key)
        else:
            return DBContext().create_query(cls.prefix, cls.index_key + '=:' + cls.index_key, **{cls.index_key: key}).first()

    @classmethod
    def save_obj(cls, obj):
        cls.save(obj.get(cls.index_key), obj)
