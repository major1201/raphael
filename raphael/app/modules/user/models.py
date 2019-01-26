# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import collections

from raphael.utils.dao.context import DBContext
from raphael.utils.dao import query
from raphael.utils import strings, cache, num, encrypt, time


class UserCacheById(cache.DBMemcached):
    prefix = 'um_user'

    @classmethod
    def actual_save(cls, key, obj):
        UserCacheByLoginid.flush_all()
        super(UserCacheById, cls).actual_save(key, obj)

    @classmethod
    def actual_remove(cls, key):
        obj = cls.get(key)
        if obj and obj.get('loginid'):
            UserCacheByLoginid.remove(obj.get('loginid'))
        super(UserCacheById, cls).actual_remove(obj)


class UserCacheByLoginid(cache.DBMemcached):
    """
    Do not use 'save' or 'remove' method in this class
    """
    prefix = 'um_user'
    index_key = 'loginid'
    with_flush = True


def get_user_byid(oid):
    return UserCacheById.get(oid)


def get_user_byloginid(logindid):
    return UserCacheByLoginid.get(logindid)


def save_user(user):
    UserCacheById.save_obj(user)


def find_users():
    return DBContext().create_query("um_user", "1=1")


def delete_user(oid):
    UserCacheById.remove(oid)


def make_password(password):
    salt = strings.uuid()
    return salt, encrypt.sha512(salt + password)


def check_user_password(user, password):
    if user is not None:
        if encrypt.sha512(user['salt'] + password) == user['password']:
            return True
    return False


class UserMenuCache(cache.AbstractMemcached):
    prefix = 'mymenu'
    with_flush = True

    @classmethod
    def actual_remove(cls, key):
        pass

    @classmethod
    def actual_save(cls, key, obj):
        pass

    @classmethod
    def actual_get(cls, user_id):
        import copy
        from operator import itemgetter

        menus = []
        ret = []
        if get_user_byid(user_id) is not None:
            my_menu_db = find_my_menu_db(user_id).order_by('name').fetch()
            menus = copy.deepcopy(my_menu_db)
        # serialize
        for menu in menus:
            if strings.is_blank(menu.get('parentid')):
                menu['children'] = []
                ret.append(menu)
        for menu in menus:
            if strings.is_not_blank(menu.get('parentid')):
                for m in ret:
                    if m['id'] == menu['parentid']:
                        m['children'].append(menu)
        for m in ret:
            m['children'] = sorted(m['children'], key=itemgetter('sort'))
        return sorted(ret, key=itemgetter('sort'))


def get_menu(oid):
    context = DBContext()
    return context.get("um_menu", oid)


def save_menu(menu):
    assert isinstance(menu, dict)
    context = DBContext()
    context.save("um_menu", menu)
    # clear my menu cache
    UserMenuCache.flush_all()


def delete_menu(oid):
    menu = get_menu(oid)
    if menu is not None:
        with DBContext() as ctx:
            ctx.delete_byid("um_menu", oid)
            # revise sort
            ctx.execute('update um_menu set sort = sort - 1 where parentid = :parentid and sort > :sort', parentid=menu['parentid'], sort=menu['sort'])
            # remove children
            ctx.execute_delete('um_menu', 'parentid = :parentid', parentid=menu['id'])
            # delete related auth
            delete_auth_byidentity(oid, "UmMenu")
            # clear my menu cache
            UserMenuCache.flush_all()


def find_menu(**params):
    sql = ['1=1']
    cond = {}
    if 'parentid' in params:
        sql.append('parentid = :parentid')
        cond['parentid'] = params['parentid']
    if 'sort' in params:
        sql.append('sort = :sort')
        cond['sort'] = num.safe_int(params['sort'])
    return DBContext().create_query("um_menu", ' and '.join(sql), **cond)


def move_menu(menu, operator):
    with DBContext() as ctx:
        changed = False
        if operator == 'top':
            if menu['sort'] != 1:
                ctx.execute('update um_menu set sort = sort + 1 where parentid = :parentid and sort < :sort', parentid=menu['parentid'], sort=menu['sort'])
                menu['sort'] = 1
                changed = True
        elif operator == 'up':
            if menu['sort'] != 1:
                ctx.execute('update um_menu set sort = sort + 1 where parentid = :parentid and sort = :sort', parentid=menu['parentid'], sort=menu['sort'] - 1)
                menu['sort'] = menu['sort'] - 1
                changed = True
        elif operator == 'down':
            if menu['sort'] != find_menu(parentid=menu['parentid']).count():
                ctx.execute('update um_menu set sort = sort - 1 where parentid = :parentid and sort = :sort', parentid=menu['parentid'], sort=menu['sort'] + 1)
                menu['sort'] = menu['sort'] + 1
                changed = True
        elif operator == 'bottom':
            if menu['sort'] != find_menu(parentid=menu['parentid']).count():
                ctx.execute('update um_menu set sort = sort - 1 where parentid = :parentid and sort > :sort', parentid=menu['parentid'], sort=menu['sort'])
                menu['sort'] = find_menu(parentid=menu['parentid']).count()
                changed = True
        if changed:
            ctx.save('um_menu', menu)
            UserMenuCache.flush_all()


class UserFunctionCache(cache.AbstractMemcached):
    @classmethod
    def actual_remove(cls, key):
        pass

    @classmethod
    def actual_save(cls, key, obj):
        pass

    @classmethod
    def actual_get(cls, key):
        sql = [
            "select f.name from um_function f",
            "right join (",
            "  select * from um_auth where sourceentity = 'UmFunction' and grantentity = 'UmUser' and grantid = :userid",
            ") a on f.id = a.sourceid"
        ]
        funcs = DBContext().create_sql_query('\n'.join(sql), userid=key).fetch()
        return [f.get('name') for f in funcs]


def get_function(oid):
    context = DBContext()
    return context.get("um_function", oid)


def save_function(obj):
    UserFunctionCache.flush_all()
    assert isinstance(obj, dict)
    context = DBContext()
    context.save("um_function", obj)


def delete_function(oid):
    if oid is not None:
        UserFunctionCache.flush_all()
        context = DBContext()
        context.delete_byid("um_function", oid)
        # delete related auth
        delete_auth_byidentity(oid, "UmFunction")


def find_functions(**params):
    return DBContext().create_query("um_function", "1=1")


def get_auth(oid):
    context = DBContext()
    return context.get("um_auth", oid)


def find_auth(**params):
    context = DBContext()
    where = ['1=1']
    argdict = {}

    for attribute in 'sourceentity', 'sourceid', 'grantentity', 'grantid':
        try:
            value = params[attribute]
            where.append('%s=:%s' % (attribute, attribute))
            argdict[attribute] = value
        except KeyError:
            pass
    for a in 'sourceentityin', 'sourceidin', 'grantentityin', 'grantidin':
        try:
            attribute = a[:-2]
            values = params[a]
            if not isinstance(values, collections.Iterable):
                raise Exception('%s should be iterable', a)
            where.append('%s in %s' % (attribute, query.escape_sequence(values)))
        except KeyError:
            pass
    return context.create_query('um_auth', ' and '.join(where), **argdict)


def save_auth(auth):
    assert isinstance(auth, dict)
    context = DBContext()
    context.save("um_auth", auth)


def get_auth_bydetail(source_id, source_entity, grant_id, grant_entity):
    context = DBContext()
    return context.create_query("um_auth", "sourceid=:sourceid and sourceentity=:sourceentity "
                                           "and grantid=:grantid and grantentity=:grantentity",
                                sourceid=source_id, sourceentity=source_entity, grantid=grant_id,
                                grantentity=grant_entity
                                ).first()


def delete_auth(oid):
    if oid is not None:
        context = DBContext()
        context.delete_byid("um_auth", oid)


def delete_auth_byidentity(oid, entity):
    context = DBContext()
    context.execute_delete("um_auth", "(sourceid = :oid and sourceentity = :entity) or "
                                      "(grantid = :oid and grantentity = :entity)",
                           oid=oid, entity=entity)


def find_menu_user_auth(menu_id):
    context = DBContext()
    sql_arr = [
        "select u.id, u.loginid, u.name, a.id authid from um_user u",
        "left join (",
        "  select id, grantid from um_auth",
        "  where sourceentity = :menuentity and sourceid = :menuid and grantentity = :userentity",
        ") a on u.id = a.grantid",
        "where u.loginid <> 'admin'"
    ]
    return context.create_sql_query("\n".join(sql_arr),
                                    menuentity="UmMenu",
                                    menuid=menu_id,
                                    userentity="UmUser"
                                    )


def find_my_menu(user_id):
    return UserMenuCache.get(user_id)


def find_my_menu_db(user_id):
    context = DBContext()
    ret = []
    user = get_user_byid(user_id)
    if user is None:
        return ret
    if user["loginid"] == "admin":
        return find_menu()
    else:
        sql = [
            "select m.* from um_menu m",
            "right join (",
            "	select * from um_auth where sourceentity = 'UmMenu' and grantentity = 'UmUser' and grantid = :userid",
            ") a on m.id = a.sourceid"
        ]
        return context.create_sql_query("\n".join(sql), userid=user_id)


def find_function_user_auth(function_id):
    context = DBContext()
    sql_arr = [
        "select u.id, u.loginid, u.name, a.id authid from um_user u",
        "left join (",
        "  select id, grantid from um_auth",
        "  where sourceentity = :functionentity and sourceid = :functionid and grantentity = :userentity",
        ") a on u.id = a.grantid",
        "where u.loginid <> 'admin'"
    ]
    return context.create_sql_query("\n".join(sql_arr),
                                    functionentity="UmFunction",
                                    functionid=function_id,
                                    userentity="UmUser"
                                    )


def check_function_auth(user_id, *func_names):
    user = get_user_byid(user_id)
    if user is not None and user['loginid'] == 'admin':
        return True
    if len(func_names) == 0:
        return True
    user_funcs = UserFunctionCache.get(user_id)
    # intersect
    func_names_set = set(func_names)
    inter = set(user_funcs) & func_names_set
    return len(inter) == len(func_names_set)


def find_umsessions(**params):
    sql_arr = ['1=1']
    cond = {}

    # token
    try:
        v = params['token']
        sql_arr.append('token = :token')
        cond['token'] = v
    except KeyError:
        pass

    # user_id
    try:
        v = params['user_id']
        sql_arr.append('user_id = :user_id')
        cond['user_id'] = v
    except KeyError:
        pass

    # expire_at
    try:
        v = params['gt_expire_at']
        sql_arr.append('expire_at > :gt_expire_at')
        cond['gt_expire_at'] = v
    except KeyError:
        pass
    try:
        v = params['lt_expire_at']
        sql_arr.append('expire_at > :lt_expire_at')
        cond['lt_expire_at'] = v
    except KeyError:
        pass

    return DBContext().create_query('um_session', ' and '.join(sql_arr), **cond)


def get_umsession(oid):
    return DBContext().get('um_session', oid)


def get_umsession_bytoken(token):
    return find_umsessions(token=token, lt_expire_at=time.utcnow()).first()


def add_umsession(user_id, duration):
    import datetime

    token = strings.uuid()
    DBContext().save('um_session', {
        'token': token,
        'user_id': user_id,
        'expire_at': time.utcnow() + datetime.timedelta(seconds=duration),
    })
    return token


def verify_umsession(token):
    return find_umsessions(token=token, lt_expire_at=time.utcnow()).count() > 0


def scrub_expired_umsessions():
    DBContext().execute_delete('um_session', 'expire_at < :now', now=time.utcnow())
