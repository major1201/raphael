# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import functools
import json
from flask import request, g, render_template
from raphael.utils import strings, encrypt, setting


def set_cookie(name, value, expire_days=None, secure=True):
    import datetime

    if not hasattr(g, 'cookies'):
        g.cookies = {}
    if expire_days == 0:
        expires = 0
    elif expire_days is not None:
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=expire_days)
    else:
        expires = None
    g.cookies[name] = {
        'value': encrypt.aes_encrypt(value, setting.conf['web']['cookie_secret']) if secure else value,
        'expires': expires
    }


def get_cookie(name, default=None, secure=True):
    try:
        rv = request.cookies[name]
        if secure:
            rv = encrypt.aes_decrypt(rv, setting.conf['web']['cookie_secret'])
    except (KeyError, ValueError):
        rv = default
    return rv


def after_this_response(f):
    if not hasattr(g, 'after_this_response'):
        g.after_this_response = []
    g.after_this_response.append(f)


def curr_user():
    try:
        return g.curr_user
    except AttributeError:
        return None


def menu(name):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            g.this_menu = name
            return f(*args, **kwargs)
        return wrapper
    return decorator


def auth(*functions):
    from .modules.user.models import check_function_auth

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if check_function_auth(curr_user()['id'], *functions):
                return f(*args, **kwargs)
            else:
                return render_template('error/noauth.html'), 403
        return wrapper
    return decorator


def make_table(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        from raphael.utils.dao.query import DaoQuery
        from collections import Iterable, Sized

        g.params = json.loads(request.form.get("params"))
        get_result = f(*args, **kwargs)

        if isinstance(get_result, DaoQuery):
            page_index = int(request.form.get("page_index"))
            page_size = int(request.form.get("page_size"))
            order_by = request.form.get("order_by")

            if strings.is_not_blank(order_by):
                get_result.order_by(order_by)
            if page_size > 0:
                res = get_result.pagination((page_index - 1) * page_size, page_size).fetch()
            else:
                res = get_result.fetch()
            # call batch
            if hasattr(g, 'table_batch'):
                res = g.table_batch(res)
            result = {
                "res": res,
                "count": get_result.count()
            }
        elif isinstance(get_result, (Iterable, Sized)):
            result = {
                "res": list(get_result),
                "count": len(get_result)
            }
        else:
            raise ValueError("get_result is not in reason.")
        return strings.to_json(result)
    return wrapper


def table_batch(f):
    g.table_batch = f
