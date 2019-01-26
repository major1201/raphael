# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from . import openldap_bp
from . import models
from raphael.app import webutils

import json

from flask import request, render_template, g
from raphael.utils import strings, logger, objects
from raphael.app.modules.user import models as um_models
from raphael.app.modules.setting import models as setting_models

from ldap3.core.exceptions import LDAPSocketOpenError, LDAPBindError

FUNC_OPENLDAP = ['SYSTEM']
LOGGER_NAME = 'OPENLDAP'


@openldap_bp.route('/users')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_users')
def users_page():
    return render_template('openldap/users.html', groups=models.search_groups())


@openldap_bp.route('/users/table', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
@webutils.make_table
def users_table():
    return models.search_users()


@openldap_bp.route('/users/new')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_users')
def users_new():
    return render_template('openldap/useredit.html', opt="NEW", groups=models.search_groups())


@openldap_bp.route('/users/edit/<cn>')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_users')
def users_edit(cn):
    user = models.get_user(cn)
    if user is None:
        user = {}
    return render_template('openldap/useredit.html', opt="EDIT", groups=models.search_groups(), **user)

@openldap_bp.route('/users/save', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def users_save():
    dn = request.form.get('dn')
    ret = {'success': False, 'error_msg': None, 'new_password': None}
    try:
        if strings.is_blank(dn):
            response = models.add_user(
                cn=request.form.get('cn'),
                sn=request.form.get('sn'),
                uid_number=request.form.get('uid'),
                gid_number=request.form.get('gid'),
                gecos=request.form.get('gecos'),
                mail=request.form.get('mail'),
                display_name=request.form.get('displayName'),
            )
            if not response:
                ret['error_msg'] = '添加失败，请查询 slapd.server 日志'
            else:
                # new password
                new_password = strings.random_str(12)
                models.reset_password(request.form.get('cn'), new_password)
                ret['success'] = True
                ret['new_password'] = new_password
        else:
            response = models.modify_user(
                cn=request.form.get('cn'),
                sn=request.form.get('sn'),
                uid_number=request.form.get('uid'),
                gid_number=request.form.get('gid'),
                gecos=request.form.get('gecos'),
                mail=request.form.get('mail'),
                display_name=request.form.get('displayName'),
            )
            if not response:
                ret['error_msg'] = '添加失败，请查询 slapd.server 日志'
            else:
                ret['success'] = True
    except LDAPBindError:
        ret['error_msg'] = '授权错误'
        return ret
    except Exception as e:
        logger.error_traceback(LOGGER_NAME)
        ret['error_msg'] = str(e)
    return strings.to_json(ret, True)


@openldap_bp.route('/users/<cn>', methods=['DELETE'])
@webutils.auth(*FUNC_OPENLDAP)
def users_delete(cn):
    if models.delete_user(cn):
        return 'success'
    else:
        return '没有找到用户'


@openldap_bp.route('/users/rstpwd/<cn>', methods=['UPDATE'])
@webutils.auth(*FUNC_OPENLDAP)
def users_reset_passwrod(cn):
    ret = {'success': False, 'new_password': None}
    try:
        new_password = strings.random_str(12)
        models.reset_password(cn, new_password)
        ret['success'] = True
        ret['new_password'] = new_password
    except:
        logger.error_traceback(LOGGER_NAME)
    return strings.to_json(ret, True)


@openldap_bp.route('/groups')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_users')
def groups_page():
    return render_template('openldap/groups.html')


@openldap_bp.route('/groups/table', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
@webutils.make_table
def groups_table():
    return models.search_groups()


@openldap_bp.route('/groups/new')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_users')
def groups_new():
    return render_template('openldap/groupedit.html', opt="NEW")


@openldap_bp.route('/groups/edit/<cn>')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_users')
def groups_edit(cn):
    group = models.get_group(cn)
    if group is None:
        group = {}
    return render_template('openldap/groupedit.html', opt="EDIT", **group)


@openldap_bp.route('/groups/save', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def groups_save():
    dn = request.form.get('dn')
    ret = {'success': False, 'error_msg': None}
    try:
        if strings.is_blank(dn):
            response = models.add_group(
                cn=request.form.get('cn'),
                gid_number=request.form.get('gid'),
            )
        else:
            response = models.modify_group(
                cn=request.form.get('cn'),
                gid_number=request.form.get('gid'),
            )
        if not response:
            ret['error_msg'] = '添加失败，请查询 slapd.server 日志'
        else:
            ret['success'] = True
    except LDAPBindError:
        ret['error_msg'] = '授权错误'
        return ret
    except Exception as e:
        logger.error_traceback(LOGGER_NAME)
        ret['error_msg'] = str(e)
    return strings.to_json(ret, True)


@openldap_bp.route('/groups/<cn>', methods=['DELETE'])
@webutils.auth(*FUNC_OPENLDAP)
def groups_delete(cn):
    if models.delete_group(cn):
        return 'success'
    else:
        return '没有找到用户组'


@openldap_bp.route('/hosts')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_hosts')
def hosts_page():
    return render_template('openldap/hosts.html')


@openldap_bp.route('/hosts/table', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
@webutils.make_table
def hosts_table():
    res = models.search_hosts()
    for item in res:
        groups = list(map(lambda x: x.get('cn'), models.search_host_groups(unique_member=item['cn'])))
        item['groups'] = groups
    return res


@openldap_bp.route('/hosts/<cn>')
@webutils.auth(*FUNC_OPENLDAP)
def hosts_get(cn):
    return strings.to_json(models.get_host(cn), True)


@openldap_bp.route('/hosts/save', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def hosts_save():
    cn = request.form.get('cn')
    ip_host_number = request.form.get('ip_host_number')
    if models.modify_host(cn, ip_host_number=ip_host_number):
        return 'success'
    else:
        return 'failed'


@openldap_bp.route('/hosts/import', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def hosts_import():
    ret = {
        'success_count': 0,
        'fail_count': 0,
        'error_items': [],
    }

    hosts_text = request.form.get('hosts')
    for host_item in hosts_text.split('\n'):
        if strings.is_blank(host_item):
            continue
        parts = host_item.split()
        if len(parts) <= 1:
            ret['error_items'].append(host_item)
            ret['fail_count'] += 1
            continue
        response = models.add_host(parts[1], parts[2:], parts[0])
        if response:
            ret['success_count'] += 1
        else:
            ret['error_items'].append(host_item)
            ret['fail_count'] += 1

    return strings.to_json(ret, True)


@openldap_bp.route('/hosts/<cn>', methods=['DELETE'])
@webutils.auth(*FUNC_OPENLDAP)
def hosts_delete(cn):
    if models.delete_host(cn):
        return 'success'
    else:
        return '没有找到主机'


@openldap_bp.route('/host_groups')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_hosts')
def host_groups_page():
    return render_template('openldap/host_groups.html')


@openldap_bp.route('/host_groups/table', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
@webutils.make_table
def host_groups_table():
    return models.search_host_groups()


@openldap_bp.route('/host_groups/<cn>')
@webutils.auth(*FUNC_OPENLDAP)
def host_groups_get(cn):
    return strings.to_json(models.get_host_group(cn), True)


@openldap_bp.route('/host_groups/save', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def host_groups_save():
    opt = request.form.get('opt')
    cn = request.form.get('cn')
    if opt == 'NEW':
        return 'success' if models.add_host_group(cn) else 'fail'
    elif opt == 'EDIT':
        try:
            unique_member = json.loads(request.form.get('unique_member'))
            return 'success' if models.modify_host_group(cn, unique_member) else '保存失败，请查阅 slapd 日志！'
        except:
            return logger.error_traceback(LOGGER_NAME)


@openldap_bp.route('/host_groups/<cn>', methods=['DELETE'])
@webutils.auth(*FUNC_OPENLDAP)
def host_groups_delete(cn):
    if models.delete_host_group(cn):
        return 'success'
    else:
        return '没有找到主机组'


@openldap_bp.route('/host_groups/edit/<cn>')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_hosts')
def host_groups_edit(cn):
    return render_template('openldap/host_group_edit.html', **models.get_host_group(cn))


@openldap_bp.route('/commands')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_commands')
def commands_page():
    return render_template('openldap/commands.html')


@openldap_bp.route('/commands/table', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
@webutils.make_table
def commands_table():
    res = models.search_commands()
    for item in res:
        groups = list(map(lambda x: x.get('cn'), models.search_command_groups(unique_member=item['cn'])))
        item['groups'] = groups
    return res


@openldap_bp.route('/commands/<cn>')
@webutils.auth(*FUNC_OPENLDAP)
def commands_get(cn):
    return strings.to_json(models.get_command(cn), True)


@openldap_bp.route('/commands/save', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def commands_save():
    cn = request.form.get('cn')
    commands = request.form.get('commands')
    if strings.is_blank(commands):
        return '命令不能为空！'
    command_list = list(filter(lambda s: strings.is_not_empty(s), map(lambda x: strings.strip_to_empty(x), commands.split('\n'))))
    _type = request.form.get('type')
    if _type == 'NEW':
        if models.add_command(cn, sudo_command=command_list):
            return 'success'
        else:
            return '保存失败'
    elif _type == 'EDIT':
        if models.modify_command(cn, sudoCommand=command_list):
            return 'success'
        else:
            return '保存失败'
    else:
        return 'Unknown type: %s' % _type


@openldap_bp.route('/commands/<cn>', methods=['DELETE'])
@webutils.auth(*FUNC_OPENLDAP)
def commands_delete(cn):
    if models.delete_command(cn):
        return 'success'
    else:
        return '没有找到命令'


@openldap_bp.route('/command_groups')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_commands')
def command_groups_page():
    return render_template('openldap/command_groups.html')


@openldap_bp.route('/command_groups/table', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
@webutils.make_table
def command_groups_table():
    return models.search_command_groups()


@openldap_bp.route('/command_groups/<cn>')
@webutils.auth(*FUNC_OPENLDAP)
def command_groups_get(cn):
    return strings.to_json(models.get_command_group(cn), True)


@openldap_bp.route('/command_groups/save', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def command_groups_save():
    opt = request.form.get('opt')
    cn = request.form.get('cn')
    if opt == 'NEW':
        return 'success' if models.add_command_group(cn) else 'fail'
    elif opt == 'EDIT':
        try:
            unique_member = json.loads(request.form.get('unique_member'))
            return 'success' if models.modify_command_group(cn, unique_member) else '保存失败，请查阅 slapd 日志！'
        except:
            return logger.error_traceback(LOGGER_NAME)


@openldap_bp.route('/command_groups/<cn>', methods=['DELETE'])
@webutils.auth(*FUNC_OPENLDAP)
def command_groups_delete(cn):
    if models.delete_command_group(cn):
        return 'success'
    else:
        return '没有找到命令组'


@openldap_bp.route('/command_groups/edit/<cn>')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_commands')
def command_groups_edit(cn):
    return render_template('openldap/command_group_edit.html', **models.get_command_group(cn))


@openldap_bp.route('/services')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_services')
def services_page():
    return render_template('openldap/services.html')


@openldap_bp.route('/services/table', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
@webutils.make_table
def services_table():
    return models.search_services()


@openldap_bp.route('/services/<cn>')
@webutils.auth(*FUNC_OPENLDAP)
def services_get(cn):
    return strings.to_json(models.get_service(cn), True)


@openldap_bp.route('/services/save', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def services_save():
    cn = request.form.get('cn')
    services = request.form.get('services')
    if strings.is_blank(services):
        return '服务不能为空！'
    service_list = list(filter(lambda s: strings.is_not_empty(s), map(lambda x: strings.strip_to_empty(x), services.split('\n'))))
    _type = request.form.get('type')
    if _type == 'NEW':
        if models.add_service(cn, authorized_service=service_list):
            return 'success'
        else:
            return '保存失败'
    elif _type == 'EDIT':
        if models.modify_service(cn, authorizedService=service_list):
            return 'success'
        else:
            return '保存失败'
    else:
        return 'Unknown type: %s' % _type


@openldap_bp.route('/services/<cn>', methods=['DELETE'])
@webutils.auth(*FUNC_OPENLDAP)
def services_delete(cn):
    if models.delete_service(cn):
        return 'success'
    else:
        return '没有找到服务组'


@openldap_bp.route('/auth')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_auth')
def auth_page():
    return render_template('openldap/auth.html', selectData={
        models.ENTITY_USER: models.list_users(),
        models.ENTITY_GROUP: models.list_groups(),
        models.ENTITY_HOST: models.list_hosts(),
        models.ENTITY_HOSTGROUP: models.list_host_groups(),
        models.ENTITY_COMMAND: models.list_commands(),
        models.ENTITY_COMMANDGROUP: models.list_command_groups(),
        models.ENTITY_SERVICE: models.list_services(),
        models.ENTITY_SERVICEPOINT: models.list_all_servicepoints(),
    })


@openldap_bp.route('/auth/table', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
@webutils.make_table
def auth_table():
    params = {
        'sourceentityin': (models.ENTITY_HOST, models.ENTITY_HOSTGROUP, models.ENTITY_COMMAND, models.ENTITY_COMMANDGROUP, models.ENTITY_SERVICE, models.ENTITY_SERVICEPOINT),
        'grantentityin': (models.ENTITY_USER, models.ENTITY_GROUP),
    }
    for a in 'sourceentity', 'sourceid', 'grantentity', 'grantid':
        val = g.params.get('q' + a)
        if strings.is_not_blank(val):
            params[a] = val
    return um_models.find_auth(**params)


@openldap_bp.route('/auth/save', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def auth_save():
    auth = {}

    # check empty value
    for k in 'sourceentity', 'sourceid', 'grantentity', 'grantid':
        val = request.form.get(k)
        if strings.is_blank(val):
            return 'empty attribute: ' + k
        auth[k] = val

    # check illegal value
    check_limit = {
        'sourceentity': (models.ENTITY_HOST, models.ENTITY_HOSTGROUP, models.ENTITY_COMMAND, models.ENTITY_COMMANDGROUP, models.ENTITY_SERVICE, models.ENTITY_SERVICEPOINT),
        'grantentity': (models.ENTITY_USER, models.ENTITY_GROUP),
    }
    for k, l in check_limit.items():
        if not objects.contains(auth[k], *l):
            return 'illegal attribute: ' + k

    # save auth object
    models.save_auth(auth)
    return 'success'


@openldap_bp.route('/auth/<oid>', methods=['DELETE'])
@webutils.auth(*FUNC_OPENLDAP)
def auth_delete(oid):
    auth = um_models.get_auth(oid)
    if auth is None:
        return "can't find auth object"

    # check illegal value
    check_limit = {
        'sourceentity': (models.ENTITY_HOST, models.ENTITY_HOSTGROUP, models.ENTITY_COMMAND, models.ENTITY_COMMANDGROUP, models.ENTITY_SERVICE, models.ENTITY_SERVICEPOINT),
        'grantentity': (models.ENTITY_USER, models.ENTITY_GROUP),
    }
    for k, l in check_limit.items():
        if not objects.contains(auth[k], *l):
            return 'illegal attribute: ' + k

    models.delete_auth(auth)
    return 'success'


@openldap_bp.route('/test')
@webutils.auth(*FUNC_OPENLDAP)
def test_connection():
    try:
        models.test_connection()
        return 'success'
    except LDAPSocketOpenError:
        return '连接错误'
    except LDAPBindError:
        return '授权错误'
    except Exception as e:
        logger.error_traceback(LOGGER_NAME)
        return str(e)


@openldap_bp.route('/skel', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def skel():
    try:
        models.construct_skeleton()
        return 'success'
    except:
        logger.error_traceback(LOGGER_NAME)
        return 'failed'


@openldap_bp.route('/setting')
@webutils.auth(*FUNC_OPENLDAP)
@webutils.menu('openldap_setting')
def setting_page():
    return render_template(
        'openldap/setting.html',
        settings=setting_models.find_settings(namelikeleft='openldap.').fetch(),
    )


@openldap_bp.route('/setting', methods=['POST'])
@webutils.auth(*FUNC_OPENLDAP)
def setting_save():
    result = {
        'success': False,
        'message': None,
        'newsettings': None,
    }
    attr_map = {
        'openldap.shadow.min': 'shadow_min',
        'openldap.shadow.max': 'shadow_max',
        'openldap.shadow.inactive': 'shadow_inactive',
        'openldap.shadow.warning': 'shadow_warning',
    }
    other_attrs = {}
    for s in json.loads(request.form.get('settings')):
        setting_models.CmSettingCache.save_obj({
            'id': s['id'],
            'name': s['name'],
            'value': s['value'],
        })
        if s['name'].find('openldap.shadow.') >= 0:
            other_attrs[attr_map[s['name']]] = s['value']

    # change user shadow attributes
    if len(other_attrs) > 0:
        try:
            for user_cn in models.list_users():
                models.modify_user(user_cn, **other_attrs)
        except:
            result['success'] = False
            result['message'] = '更改用户属性时错误'
            return strings.to_json(result, True)

    result['success'] = True
    result['newsettings'] = setting_models.find_settings(namelikeleft='openldap.').fetch()
    return strings.to_json(result, True)
