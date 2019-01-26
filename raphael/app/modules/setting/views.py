# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from . import setting_bp
from .models import find_settings, get_setting, CmSettingCache
from raphael.app import webutils
from flask import request, render_template, g
from raphael.utils import strings

FUNC_SETTING = ['SYSTEM']


@setting_bp.route('/')
@webutils.auth(*FUNC_SETTING)
@webutils.menu('cm.setting')
def index():
    return render_template('cm/setting.html')


@setting_bp.route('/table', methods=['POST'])
@webutils.auth(*FUNC_SETTING)
@webutils.make_table
def table():
    cond = {}
    qname = g.params.get('qname')
    if strings.is_not_blank(qname):
        cond['namelike'] = qname
    return find_settings(**cond)


@setting_bp.route('/save', methods=['POST'])
@webutils.auth(*FUNC_SETTING)
def save():
    oid = strings.strip_to_none(request.form.get('id', None))
    name = request.form.get('name', None)
    if strings.is_blank(name):
        return 'Name cannot be blank'
    # check duplication
    cond = {'name': name}
    if strings.is_not_blank(oid):
        cond['notid'] = oid
    if find_settings(**cond).count() > 0:
        return 'Name has already been exist!'
    CmSettingCache.save_obj({
        'id': oid,
        'name': name,
        'value': request.form.get('value', None)
    })
    return 'success'


@setting_bp.route('/<oid>')
@webutils.auth(*FUNC_SETTING)
def get(oid):
    o = get_setting(oid)
    return strings.to_json(o)


@setting_bp.route('/<oid>', methods=['DELETE'])
@webutils.auth(*FUNC_SETTING)
def remove(oid):
    o = get_setting(oid)
    if not o:
        return 'Item not exist: ' + oid
    CmSettingCache.remove(o['name'])
    return 'success'
