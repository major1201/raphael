# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from . import func_bp
from ..user.models import get_function, find_functions, save_function, delete_function, find_function_user_auth, UserFunctionCache, get_auth_bydetail, save_auth, delete_auth, get_user_byid
from raphael.app import webutils, trstatus
from flask import request, render_template, g
from raphael.utils import strings, objects

FUNC_FUNC = ['SYSTEM']


@func_bp.route('/')
@webutils.auth(*FUNC_FUNC)
@webutils.menu('function')
def index():
    return render_template('um/function.html')


@func_bp.route('/table', methods=['POST'])
@webutils.auth(*FUNC_FUNC)
@webutils.make_table
def table():
    return find_functions()


@func_bp.route('/save', methods=['POST'])
@webutils.auth(*FUNC_FUNC)
def save():
    oid = request.form.get("id")
    func = {}
    if strings.is_not_blank(oid):
        func = get_function(oid)
        if func is None:
            func = {}
    func["name"] = request.form.get("name")
    save_function(func)
    return "success"


@func_bp.route('/get', methods=['POST'])
@webutils.auth(*FUNC_FUNC)
def get():
    uid = request.form.get("id")
    if strings.is_not_blank(uid):
        func = get_function(uid)
        if func is not None:
            return strings.to_json(func)
    return "failed"


@func_bp.route('/delete', methods=['POST'])
@webutils.auth(*FUNC_FUNC)
def delete():
    uid = request.form.get("id")
    delete_function(uid)
    return "success"


@func_bp.route('/auth', methods=['POST'])
@webutils.auth(*FUNC_FUNC)
@webutils.make_table
def auth():
    @webutils.table_batch
    def batch(res):
        for record in res:
            if record["authid"] is None:
                record["_trstatus"] = trstatus.DANGER
            else:
                record["_trstatus"] = trstatus.SUCCESS
        return res
    return find_function_user_auth(g.params["functionid"])


@func_bp.route('/setauth', methods=['POST'])
@webutils.auth(*FUNC_FUNC)
def set_auth():
    function_id = request.form.get("functionId")
    user_id = request.form.get("userId")
    _type = int(request.form.get("type"))
    if strings.is_blank(function_id) or strings.is_blank(user_id) or not objects.contains(_type, 1, 2):
        return "参数错误！"
    func = get_function(function_id)
    if func is None:
        return "功能不存在"

    user = get_user_byid(user_id)
    if user is None:
        return "用户不存在"
    _set_auth(function_id, user_id, _type)
    return "success"


def _set_auth(function_id, user_id, _type):
    _auth = get_auth_bydetail(function_id, "UmFunction", user_id, "UmUser")
    if _type == 1:
        if _auth is None:
            _auth = {"sourceid": function_id, "sourceentity": "UmFunction", "grantid": user_id, "grantentity": "UmUser"}
            save_auth(_auth)
    else:
        if _auth is not None:
            delete_auth(_auth["id"])
    UserFunctionCache.remove(user_id)
