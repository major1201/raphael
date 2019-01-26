# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from . import main
from flask import request, render_template
from raphael.app.webutils import set_cookie, get_cookie
from raphael.utils import strings, setting
from raphael.app.modules.user.models import get_user_byloginid, check_user_password, add_umsession


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/ip')
def ip():
    return request.remote_addr


@main.route('/login')
def login():
    set_cookie('AUTHTOKEN', '', 0)
    ctx = {
        'username': strings.strip_to_empty(get_cookie('USERNAME')),
        'sourceurl': request.args.get('url'),
        'otpenabled': setting.get_bool('system.otp.enabled')
    }
    return render_template('login.html', **ctx)


@main.route('/login/login', methods=['POST'])
def login_ajax():
    import pyotp

    username = request.form.get("username")
    password = request.form.get("password")
    remember = request.form.get("remember", "") == 'true'

    user = get_user_byloginid(username)
    if not user:
        return 'failed'
    # otp verify
    if setting.get_bool('system.otp.enabled'):
        if strings.is_not_blank(user.get('otpsecret')):
            totp = pyotp.TOTP(user.get('otpsecret'))
            if not totp.verify(request.form.get('otp', None)):
                return 'failed'
    if check_user_password(user, password):
        set_cookie('AUTHTOKEN', add_umsession(user['id'], setting.get_int('system.session.timeout', 86400)), 10)
        if remember:
            set_cookie('USERNAME', user["loginid"], 15)
        else:
            set_cookie('USERNAME', '', 0)
        return "success"
    return 'failed'


@main.route('/login/signout', methods=['POST'])
def signout():
    set_cookie('AUTHTOKEN', '', 0)
    return 'success'
