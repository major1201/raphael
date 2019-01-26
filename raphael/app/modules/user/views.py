# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from . import user_bp
import os
import copy
from flask import request, render_template, send_from_directory
from raphael.app import webutils
from raphael.utils import strings, setting, net
from . import models as um

FUNC_USER = ['SYSTEM']


@user_bp.route('/')
@webutils.auth(*FUNC_USER)
@webutils.menu('user')
def index():
    return render_template('um/user.html')


@user_bp.route('/table', methods=['POST'])
@webutils.auth(*FUNC_USER)
@webutils.make_table
def table():
    from .models import find_users
    return find_users()


@user_bp.route('/save', methods=['POST'])
@webutils.auth(*FUNC_USER)
def save():
    import pyotp

    oid = request.form.get("inid")
    login_id = request.form.get("inloginid")

    user = {}
    if strings.is_not_blank(oid):
        user = um.get_user_byid(oid)
        if user is None:
            user = {}
    else:  # 判断重复
        duser = um.get_user_byloginid(login_id)
        if duser is not None:
            return "用户登录ID已经存在！"
    user["loginid"] = login_id
    user["name"] = request.form.get("inname")
    password = request.form.get("inpassword", None)
    if strings.is_not_blank(password):
        # 不为空则重置密码
        salt, enpassword = um.make_password(password)
        user["salt"] = salt
        user["password"] = enpassword
    user['email'] = request.form.get('email', None)
    if strings.is_blank(oid):
        user['otpsecret'] = pyotp.random_base32()
    um.save_user(user)
    return "success"


@user_bp.route('/get', methods=['POST'])
@webutils.auth(*FUNC_USER)
def get():
    uid = request.form.get("id")
    if strings.is_not_blank(uid):
        user = um.get_user_byid(uid)
        if user is not None:
            user.pop('password', None)
            user.pop('salt', None)
            return strings.to_json(user)
    return "failed"


@user_bp.route('/delete', methods=['POST'])
@webutils.auth(*FUNC_USER)
def delete():
    uid = request.form.get("id")
    um.delete_user(uid)
    return "success"


@user_bp.route('/profile')
@webutils.auth(*FUNC_USER)
def profile():
    user = webutils.curr_user()
    if not user or user.get('loginid') == 'guest':
        return {'msg': "failed", 'user': '{}'}
    user = copy.deepcopy(user)
    user.pop('password', None)
    user.pop('salt', None)
    return render_template('um/profile.html', **{'msg': 'success', 'user': strings.to_json(user, True)})


@user_bp.route('/changepassword', methods=['POST'])
def changepassword():
    oldpwd = request.form.get('oldpwd', None)
    newpwd = request.form.get('newpwd', None)
    if strings.is_empty(oldpwd) or strings.is_empty(newpwd):
        return "Password can't be blank!"
    user = webutils.curr_user()
    if not user:
        return 'User not found'
    if user.get('loginid') == 'guest':
        return 'You cannot change password for Guest!'
    if not um.check_user_password(user, oldpwd):
        return 'Old password id wrong!'
    user = copy.deepcopy(user)
    salt, enpassword = um.make_password(newpwd)
    user["salt"] = salt
    user["password"] = enpassword
    um.save_user(user)
    return 'success'


@user_bp.route('/otp/regensecret', methods=['POST'])
@webutils.auth(*FUNC_USER)
def regenerate_secret():
    user_id = request.form.get('userid', None)
    user = um.get_user_byid(user_id)
    if not user:
        return 'Cannot find user!'

    import pyotp
    user['otpsecret'] = pyotp.random_base32()
    um.save_user(user)
    return 'success'


@user_bp.route('/otp/qrcode')
@webutils.auth(*FUNC_USER)
def qrcode():
    user_id = request.args.get('userid', None)
    user = um.get_user_byid(user_id)
    if not user:
        return None
    if strings.is_blank(user.get('otpsecret')):
        return None

    import pyotp
    import pyqrcode
    totp = pyotp.TOTP(user.get('otpsecret'))
    uri = totp.provisioning_uri(user['loginid'])
    _qrcode = pyqrcode.create(uri)
    svg_path = os.path.join(setting.get('system.tempdir'), user_id + '.svg')
    _qrcode.svg(svg_path)

    @webutils.after_this_response  # clear temp file on finish
    def remove_tmp_file():
        if strings.is_not_blank(user_id):
            try:
                os.remove(svg_path)
            except:
                pass

    return send_from_directory(setting.get('system.tempdir'), user_id + '.svg', mimetype=net.get_content_type_by_ext('.svg'))
