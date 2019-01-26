# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from . import menu_bp
from ..user.models import get_menu, find_menu, save_menu, delete_menu, move_menu, find_menu_user_auth, get_user_byid, get_auth_bydetail, save_auth, delete_auth, UserMenuCache
from raphael.app import webutils, trstatus
from flask import request, render_template, g
from raphael.utils import strings, num, objects

FUNC_MENU = ['SYSTEM']


@menu_bp.route('/')
@webutils.auth(*FUNC_MENU)
@webutils.menu('menu')
def index():
    return render_template('um/menu.html')


@menu_bp.route('/table', methods=['POST'])
@webutils.auth(*FUNC_MENU)
@webutils.make_table
def table():
    parentid = strings.strip_to_empty(g.params.get('qparentid'))
    return find_menu(parentid=parentid)


@menu_bp.route('/save', methods=['POST'])
@webutils.auth(*FUNC_MENU)
def save():
    oid = request.form.get("id")
    parentid = strings.strip_to_empty(request.form.get('parentid', ''))
    menu = {}
    if strings.is_not_blank(oid):
        menu = get_menu(oid)
        if menu is None:
            menu = {}
    else:
        menu['sort'] = find_menu(parentid=parentid).count() + 1
    menu["name"] = request.form.get("name", '')
    menu['type'] = num.safe_int(request.form.get('type', 0))
    menu["url"] = request.form.get("url", None)
    menu["target"] = request.form.get("target", None)
    menu['parentid'] = parentid
    menu['icon'] = request.form.get('icon', '')
    menu['mark'] = request.form.get('mark', '')
    save_menu(menu)
    return "success"


@menu_bp.route('/get', methods=['POST'])
@webutils.auth(*FUNC_MENU)
def get():
    uid = request.form.get("id")
    if strings.is_not_blank(uid):
        menu = get_menu(uid)
        if menu is not None:
            return strings.to_json(menu)
    return "failed"


@menu_bp.route('/delete', methods=['POST'])
@webutils.auth(*FUNC_MENU)
def delete():
    uid = request.form.get("id")
    delete_menu(uid)
    return "success"


@menu_bp.route('/<menu_id>/move/<operator>', methods=['POST'])
@webutils.auth(*FUNC_MENU)
def move(menu_id, operator):
    if not objects.contains(operator, 'top', 'up', 'down', 'bottom'):
        return 'Invalid operator: ' + operator
    menu = get_menu(menu_id)
    if not menu:
        return 'Menu not found: ' + menu_id
    move_menu(menu, operator)
    return 'success'


@menu_bp.route('/auth', methods=['POST'])
@webutils.auth(*FUNC_MENU)
@webutils.make_table
def get_auth():
    @webutils.table_batch
    def batch(res):
        for record in res:
            if record["authid"] is None:
                record["_trstatus"] = trstatus.DANGER
            else:
                record["_trstatus"] = trstatus.SUCCESS
        return res
    return find_menu_user_auth(g.params["menuid"])


@menu_bp.route('/setauth', methods=['POST'])
@webutils.auth(*FUNC_MENU)
def set_auth():
    menu_id = request.form.get("menuId")
    user_id = request.form.get("userId")
    _type = int(request.form.get("type"))
    if strings.is_blank(menu_id) or strings.is_blank(user_id) or not objects.contains(_type, 1, 2):
        return "参数错误！"
    menu = get_menu(menu_id)
    if menu is None:
        return "菜单不存在"

    user = get_user_byid(user_id)
    if user is None:
        return "用户不存在"
    _set_auth(menu_id, user_id, _type)
    return "success"


def _set_auth(menu_id, user_id, _type):
    auth = get_auth_bydetail(menu_id, "UmMenu", user_id, "UmUser")
    if _type == 1:
        if auth is None:
            auth = {"sourceid": menu_id, "sourceentity": "UmMenu", "grantid": user_id, "grantentity": "UmUser"}
            save_auth(auth)
    else:
        if auth is not None:
            delete_auth(auth["id"])
    UserMenuCache.remove(user_id)
