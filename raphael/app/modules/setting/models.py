# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from raphael.utils import cache
from raphael.utils.dao.context import DBContext

CM_SETTING = 'cm_setting'


class CmSettingCache(cache.DBMemcached):
    prefix = CM_SETTING
    index_key = 'name'
    with_flush = True


def get_setting(oid):
    return DBContext().get(CM_SETTING, oid)


def find_settings(**params):
    where = ['1=1']
    cond = {}
    if 'name' in params:
        where.append('name = :name')
        cond['name'] = params['name']
    if 'namelike' in params:
        where.append('name like :namelike')
        cond['namelike'] = '%' + params['namelike'] + '%'
    if 'namelikeleft' in params:
        where.append('name like :namelikeleft')
        cond['namelikeleft'] = params['namelikeleft'] + '%'
    if 'value' in params:
        where.append('value = :value')
        cond['value'] = params['value']
    if 'notid' in params:
        where.append('id != :notid')
        cond['notid'] = params['notid']
    return DBContext().create_query(CM_SETTING, ' and '.join(where), **cond)
