# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from . import main
from raphael.app import webutils
from flask import request, g, Response
from raphael.utils import setting, logger, strings


@main.before_app_request
def user_session():
    if request.endpoint is None:
        return

    from ...modules.user.models import get_user_byid, get_user_byloginid, get_umsession_bytoken
    try:
        token = webutils.get_cookie('AUTHTOKEN')
        if strings.is_not_blank(token):
            session = get_umsession_bytoken(token)
            if session is not None:
                user = get_user_byid(session['user_id'])
                if user is not None:
                    g.curr_user = user
                    return
            webutils.set_cookie('AUTHTOKEN', '', expire_days=0)
        g.curr_user = get_user_byloginid('guest')
    except:
        logger.error_traceback()


@main.app_context_processor
def default_template_context():
    from ..user.models import find_my_menu
    if request.endpoint is None:
        return {}
    user = webutils.curr_user()
    is_logged_in = user['loginid'] != 'guest'
    # my menu
    mymenu = find_my_menu(user['id'])
    if hasattr(g, 'this_menu'):
        for first_level in mymenu:
            if first_level.get('mark') == g.this_menu:
                first_level['active'] = True
                break
            for second_level in first_level['children']:
                if second_level.get('mark') == g.this_menu:
                    second_level['active'] = True
                    first_level['active'] = True
                    break
    return {
        'pageurl': request.url,
        'isloggedin': is_logged_in,
        'username': user['name'],
        'mymenu': mymenu,
        'displaytitle': setting.get('system.display.title'),
        'displayfooter': setting.get('system.display.footer')
    }


@main.after_app_request
def process_cookie(response):
    assert isinstance(response, Response)
    if hasattr(g, 'cookies'):
        for name, cookie in g.cookies.items():
            response.set_cookie(
                key=name,
                value=cookie['value'],
                expires=cookie['expires'],
                path='/',
                domain=None
            )
    return response


@main.after_app_request
def remember_status_code(response):
    g.status_code = response.status_code
    return response


@main.teardown_app_request
def write_log(e):
    if e is not None:
        logger.error_traceback()
    log_arr = (str(g.status_code), request.method, request.full_path, '(' + request.remote_addr + ')')
    logger.info(' '.join(log_arr), 'WEB')


@main.teardown_app_request
def run_after_this_response(e):
    if e is not None:
        return
    if hasattr(g, 'after_this_response'):
        for f in g.after_this_response:
            try:
                f()
            except:
                logger.error_traceback('WEB')
