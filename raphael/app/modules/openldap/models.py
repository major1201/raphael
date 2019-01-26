# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import functools

from flask import g
from ldap3.utils.conv import escape_filter_chars

from raphael.utils import setting, objects
from raphael.app.modules.user import models as um_models
from .openldap import OpenLDAPSession, OpenLDAPEvents

LOGGER_NAME = 'OPENLDAP'

ENTITY_USER = 'OpenldapUser'
ENTITY_GROUP = 'OpenldapGroup'
ENTITY_HOST = 'OpenldapHost'
ENTITY_HOSTGROUP = 'OpenldapHostGroup'
ENTITY_COMMAND = 'OpenldapCommand'
ENTITY_COMMANDGROUP = 'OpenldapCommandGroup'
ENTITY_SERVICE = 'OpenldapService'
ENTITY_SERVICEPOINT = 'OpenldapServicePoint'


class MyOpenLDAPEvents(OpenLDAPEvents):
    """
    事件处理逻辑：
    - 创建用户：  指定了分组时，应用该用户的 hosts + commands + services
    - 更新用户：  更新分组时，应用该用户的 hosts + commands + services
    - 删除用户：  删除数据库中该用户的授权条目
    - 创建用户组：无需操作
    - 更新用户组：gid 更改后，原组成员、新组成员更新 hosts + commands + services
    - 删除用户组：删除数据库中该组的授权条目；更新该组中所有 users 的 hosts + commands + services
    - 创建主机：  无需操作
    - 更新主机：  cn 原则上不允许更改，无需操作
    - 删除主机：  数据库中删除该 host 的授权条目；搜索所有有该 host 的用户条目，删掉该 host 条目
    - 创建主机组：无需操作
    - 更新主机组：cn 更新：数据库中更新该组的 dn 即可；新 host 加入组：更新所有授权该组的所有用户和所有组中用户的 hosts
    - 删除主机组：删除数据库中该组的授权条目；授权该组的所有用户和所有组中用户的 hosts 更新
    - 创建命令：  无需操作
    - 更新命令：  重建授权该命令和授权存在该命令的命令组的用户和用户组的 commands
    - 删除命令：  删除数据库中该命令的授权条目；重新授权原该命令和相关命令组的用户和用户组的 commands
    - 创建命令组：无需操作
    - 更新命令组：更新授权相关的用户和用户组的 commands
    - 删除命令组：删除数据库中该组的授权条目；授权该组的所有用户和用户组中用户的 commands 更新
    - 创建服务：  无需操作
    - 更新服务：  重建相关授权用户和用户组的 services
    - 删除服务：  数据库中删除相关授权条目；重建相关授权用户和用户组的 services
    """

    @staticmethod
    def _get_users_by_source(sourceentity, sourceid):
        auths = um_models.find_auth(sourceentity=sourceentity, sourceid=sourceid).fetch()
        users = set()
        for auth in auths:
            if auth['grantentity'] == ENTITY_USER:
                users.add(auth['grantid'])
            elif auth['grantentity'] == ENTITY_GROUP:
                _users = search_users(attributes=['cn'], group=auth['grantid'])
                users.update(set(map(lambda x: x['cn'], _users)))
        return users

    def on_user_created(self, dn, object_class=None, attributes=None):
        if str(attributes.get('gidNumber')) != '100':
            update_users_auth_attr(
                attributes['cn'],
                update_host=True,
                update_command=True,
                update_service=True,
            )

    def on_user_modified(self, dn, changes, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        old_gid = oldobject.get('gidNumber')
        cn = self.session.extract_cn(dn)
        user = self.session.get_user(cn, attributes=['cn', 'gidNumber'])
        if user is not None and user.get('gidNumber') != old_gid:
            update_users_auth_attr(
                cn,
                update_host=True,
                update_command=True,
                update_service=True,
            )

    def on_user_deleted(self, dn, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        cn = self.session.extract_cn(dn)
        um_models.delete_auth_byidentity(cn, ENTITY_USER)

    def on_group_created(self, dn, object_class=None, attributes=None):
        pass

    def on_group_modified(self, dn, changes, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        old_gid = oldobject.get('gidNumber')
        cn = self.session.extract_cn(dn)
        group = self.session.get_group(cn, attributes=['cn', 'gidNumber'])
        if group is not None and group.get('gidNumber') != old_gid:
            # 原 gid 的所有用户
            update_users_auth_attr(
                *list(map(lambda x: x['cn'], search_users(attributes=['cn'], gid_number=old_gid))),
                update_host=True,
                update_command=True,
                update_service=True
            )
            # 新 gid 的所有用户
            update_group_auth_attr(
                cn,
                update_host=True,
                update_command=True,
                update_service=True,
            )

    def on_group_deleted(self, dn, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        cn = self.session.extract_cn(dn)
        # 删除数据库中该组的条目
        um_models.delete_auth_byidentity(cn, ENTITY_GROUP)

        # 重建该组中的所有用户授权
        old_gid = oldobject.get('gidNumber')
        update_users_auth_attr(
            *list(map(lambda x: x['cn'], search_users(attributes=['cn'], gid_number=old_gid))),
            update_host=True,
            update_command=True,
            update_service=True
        )

    def on_host_created(self, dn, object_class=None, attributes=None):
        pass

    def on_host_modified(self, dn, changes, oldobject):
        pass

    def on_host_deleted(self, dn, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        cn = self.session.extract_cn(dn)
        # 删除数据库中该 host 的条目
        um_models.delete_auth_byidentity(cn, ENTITY_HOST)

        # 重建含该 host 的所有用户
        update_users_auth_attr(
            *list(map(lambda x: x['cn'], search_users(attributes=['cn'], host=cn))),
            update_host=True
        )

    def on_hostgroup_created(self, dn, object_class=None, attributes=None):
        pass

    def on_hostgroup_modified(self, dn, changes, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        old_members = oldobject.get('uniqueMember')
        cn = self.session.extract_cn(dn)
        hostgroup = self.session.get_host_group(cn, attributes=['cn', 'uniqueMember'])
        new_members = hostgroup.get('uniqueMember')

        # if the hosts are changed or not
        if old_members is None and new_members is None:
            changed_flag = False
        elif old_members is None or new_members is None:
            changed_flag = True
        else:
            changed_flag = frozenset(old_members) != frozenset(new_members)
        if not changed_flag:
            return

        # if changed
        update_users_auth_attr(*self._get_users_by_source(ENTITY_HOSTGROUP, cn), update_host=True)

    def on_hostgroup_deleted(self, dn, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        cn = self.session.extract_cn(dn)

        # 获取原有授权的用户
        users = self._get_users_by_source(ENTITY_HOSTGROUP, cn)

        # 删数据库中的相关授权
        um_models.delete_auth_byidentity(cn, ENTITY_HOSTGROUP)

        # 重新授权
        update_users_auth_attr(*users, update_host=True)

    def on_command_created(self, dn, object_class=None, attributes=None):
        pass

    def on_command_modified(self, dn, changes, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        cn = self.session.extract_cn(dn)
        old_commands = oldobject.get('sudoCommand')
        command = get_command(cn)
        new_commands = command.get('sudoCommand')

        # if the commands are changed or not
        if old_commands is None and new_commands is None:
            changed_flag = False
        elif old_commands is None or new_commands is None:
            changed_flag = True
        else:
            changed_flag = frozenset(old_commands) != frozenset(new_commands)
        if not changed_flag:
            return

        # if changed
        affected_users = self._get_users_by_source(ENTITY_COMMAND, cn)
        for gp in search_command_groups(attributes=['cn'], unique_member=cn):
            affected_users.update(self._get_users_by_source(ENTITY_COMMANDGROUP, gp['cn']))
        update_users_auth_attr(*affected_users, update_command=True)

    def on_command_deleted(self, dn, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        cn = self.session.extract_cn(dn)

        involved_users = self._get_users_by_source(ENTITY_COMMAND, cn)

        # 删除数据库中该 command 的条目
        um_models.delete_auth_byidentity(cn, ENTITY_COMMAND)

        # 重建含该 command 的所有用户
        update_users_auth_attr(*involved_users, update_command=True)

    def on_commandgroup_created(self, dn, object_class=None, attributes=None):
        pass

    def on_commandgroup_modified(self, dn, changes, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        old_members = oldobject.get('uniqueMember')
        cn = self.session.extract_cn(dn)
        commandgroup = self.session.get_command_group(cn, attributes=['cn', 'uniqueMember'])
        new_members = commandgroup.get('uniqueMember')

        # if the commads are changed or not
        if old_members is None and new_members is None:
            changed_flag = False
        elif old_members is None or new_members is None:
            changed_flag = True
        else:
            changed_flag = frozenset(old_members) != frozenset(new_members)
        if not changed_flag:
            return

        # if changed
        update_users_auth_attr(*self._get_users_by_source(ENTITY_COMMANDGROUP, cn), update_command=True)

    def on_commandgroup_deleted(self, dn, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        cn = self.session.extract_cn(dn)

        # 获取原有授权的用户
        users = self._get_users_by_source(ENTITY_COMMANDGROUP, cn)

        # 删数据库中的相关授权
        um_models.delete_auth_byidentity(cn, ENTITY_COMMANDGROUP)

        # 重新授权
        update_users_auth_attr(*users, update_command=True)

    def on_service_created(self, dn, object_class=None, attributes=None):
        pass

    def on_service_modified(self, dn, changes, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        cn = self.session.extract_cn(dn)
        old_services = oldobject.get('authorizedService')
        service = get_service(cn)
        new_services = service.get('authorizedService')

        # if the services are changed or not
        if old_services is None and new_services is None:
            changed_flag = False
        elif old_services is None or new_services is None:
            changed_flag = True
        else:
            changed_flag = frozenset(old_services) != frozenset(new_services)
        if not changed_flag:
            return

        # if changed
        update_users_auth_attr(*self._get_users_by_source(ENTITY_SERVICE, cn), update_service=True)

    def on_service_deleted(self, dn, oldobject):
        assert isinstance(self.session, OpenLDAPSession)
        cn = self.session.extract_cn(dn)

        involved_users = self._get_users_by_source(ENTITY_SERVICE, cn)

        # 删除数据库中该 service 的条目
        um_models.delete_auth_byidentity(cn, ENTITY_SERVICE)

        # 重建含该 service 的所有用户
        update_users_auth_attr(*involved_users, update_service=True)


def openldap_session(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(g, 'openldap_session'):
            g.openldap_session = OpenLDAPSession(
                uri=setting.get('openldap.uri'),
                basedn=setting.get('openldap.basedn'),
                manager=setting.get('openldap.manager'),
                passwd=setting.get('openldap.passwd'),
                start_tls=setting.get_bool('openldap.start_tls'),
                ou_people=setting.get('openldap.ou_people', 'people'),
                ou_groups=setting.get('openldap.ou_groups', 'groups'),
                ou_hosts=setting.get('openldap.ou_hosts', 'hosts'),
                ou_host_groups=setting.get('openldap.ou_host_groups', 'hostGroups'),
                ou_commands=setting.get('openldap.ou_commands', 'commands'),
                ou_command_groups=setting.get('openldap.ou_command_groups', 'commandGroups'),
                ou_services=setting.get('openldap.ou_services', 'services'),
                event_handlers=[MyOpenLDAPEvents()],
            )
        with g.openldap_session:
            return f(*args, **kwargs)
    return wrapper


@openldap_session
def test_connection():
    pass


@openldap_session
def construct_skeleton():
    assert isinstance(g.openldap_session, OpenLDAPSession)
    g.openldap_session.construct_skeleton()


@openldap_session
def search_users(attributes=None, **params):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    condition_list = ['(objectClass=*)', '(objectClass=person)']

    if attributes is None:
        attributes = 'cn', 'sn', 'uidNumber', 'gidNumber', 'gecos', 'mail', 'displayName', 'shadowLastChange'

    if 'cn' in params:
        condition_list.append('(cn=%s)' % escape_filter_chars(params['cn']))
    if 'cnlike' in params:
        condition_list.append('(cn=*%s*)' % escape_filter_chars(params['cnlike']))
    if 'cnin' in params:
        _cns = []
        for cn in params['cnin']:
            _cns.append('(cn=%s)' % escape_filter_chars(cn))
        condition_list.append('(|%s)' % ''.join(_cns))
    if 'gid_number' in params:
        condition_list.append('(gidNumber=%s)' % escape_filter_chars(params['gid_number']))
    if 'group' in params:
        gid = get_group(params['group'])['gidNumber']
        condition_list.append('(gidNumber=%s)' % escape_filter_chars(gid))
    if 'host' in params:
        condition_list.append('(host=%s)' % escape_filter_chars(params['host']))
    condition_str = '(&' + ''.join(condition_list) + ')'
    return g.openldap_session.search_users(condition_str, attributes)


def list_users(key='cn'):
    return list(map(lambda x: x[key], search_users([key])))


def get_user(cn):
    users = search_users(cn=cn)
    return users[0] if len(users) > 0 else None


@openldap_session
def add_user(cn, sn, uid_number, gid_number=100, gecos=None, mail=None, display_name=None, force_change_password=False):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    response = g.openldap_session.add_user(
        cn, sn, uid_number, gid_number, gecos, mail, display_name,
        shadow_min=setting.get_int('openldap.shadow.min'),
        shadow_max=setting.get_int('openldap.shadow.max'),
        shadow_inactive=setting.get_int('openldap.shadow.inactive'),
        shadow_warning=setting.get_int('openldap.shadow.warning'),
        shadow_last_change=0 if force_change_password else None,
    )
    return response


@openldap_session
def modify_user(cn, sn=None, uid_number=None, **other_attrs):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.modify_user(cn, sn=sn, uid_number=uid_number, **other_attrs)


@openldap_session
def delete_user(cn):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.delete_user(cn)


@openldap_session
def reset_password(cn, new_password):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    g.openldap_session.reset_password(cn, new_password)


@openldap_session
def search_groups(attributes=None, **params):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    condition_list = ['(objectClass=*)', '(objectClass=posixGroup)']

    if attributes is None:
        attributes = 'cn', 'gidNumber'

    if 'cn' in params:
        condition_list.append('(cn=%s)' % escape_filter_chars(params['cn']))
    if 'cnlike' in params:
        condition_list.append('(cn=*%s*)' % escape_filter_chars(params['cnlike']))
    if 'gid_number' in params:
        condition_list.append('(gidNumber=%s)' % escape_filter_chars(params['gid_number']))
    if 'gid_number_in' in params:
        _gids = []
        for gid in params['gid_number_in']:
            _gids.append('(gidNumber=%s)' % escape_filter_chars(gid))
        condition_list.append('(|%s)' % ''.join(_gids))

    condition_str = '(&' + ''.join(condition_list) + ')'
    return g.openldap_session.search_groups(condition_str, attributes)


def list_groups(key='cn'):
    return list(map(lambda x: x[key], search_groups([key])))


def get_group(cn):
    groups = search_groups(cn=cn)
    return groups[0] if len(groups) > 0 else None


@openldap_session
def add_group(cn, gid_number):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.add_group(cn, gid_number)


@openldap_session
def modify_group(cn, gid_number=None, **other_attrs):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.modify_group(cn, gid_number=gid_number, **other_attrs)


@openldap_session
def delete_group(cn):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.delete_group(cn)


@openldap_session
def search_hosts(attributes=None, **params):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    condition_list = ['(objectClass=*)', '(objectClass=device)']

    if attributes is None:
        attributes = 'cn', 'ipHostNumber'

    if 'cn' in params:
        condition_list.append('(cn=%s)' % escape_filter_chars(params['cn']))
    if 'cnlike' in params:
        condition_list.append('(cn=*%s*)' % escape_filter_chars(params['cnlike']))

    condition_str = '(&' + ''.join(condition_list) + ')'
    return g.openldap_session.search_hosts(condition_str, attributes)


def list_hosts(key='cn'):
    return list(map(lambda x: x[key], search_hosts([key])))


def get_host(cn):
    hosts = search_hosts(cn=cn)
    return hosts[0] if len(hosts) > 0 else None


@openldap_session
def add_host(cn, cn_list=None, ip_host_number=None):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.add_host(cn, cn_list=cn_list, ip_host_number=ip_host_number)


@openldap_session
def modify_host(cn, **other_attrs):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.modify_host(cn, **other_attrs)


@openldap_session
def delete_host(cn):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.delete_host(cn)


@openldap_session
def search_host_groups(attributes=None, **params):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    condition_list = ['(objectClass=*)', '(objectClass=groupOfUniqueNames)']

    if attributes is None:
        attributes = 'cn', 'uniqueMember'

    if 'cn' in params:
        condition_list.append('(cn=%s)' % escape_filter_chars(params['cn']))
    if 'cnlike' in params:
        condition_list.append('(cn=*%s*)' % escape_filter_chars(params['cnlike']))
    if 'unique_member' in params:
        condition_list.append('(uniqueMember=%s)' % g.openldap_session.assemble_host_dn(escape_filter_chars(params['unique_member'])))

    condition_str = '(&' + ''.join(condition_list) + ')'
    results = g.openldap_session.search_host_groups(condition_str, attributes)
    for result in results:
        if 'uniqueMember' in result:
            result['uniqueMember'] = list(map(g.openldap_session.extract_cn, result['uniqueMember']))
    return results


def list_host_groups(key='cn'):
    return list(map(lambda x: x[key], search_host_groups([key])))


def get_host_group(cn):
    host_groups = search_host_groups(cn=cn)
    return host_groups[0] if len(host_groups) > 0 else None


@openldap_session
def add_host_group(cn):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.add_host_group(cn)


@openldap_session
def modify_host_group(cn, unique_member=None):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.modify_host_group(cn, unique_member)


@openldap_session
def delete_host_group(cn):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.delete_host_group(cn)


@openldap_session
def search_commands(attributes=None, **params):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    condition_list = ['(objectClass=*)', '(objectClass=sudoRole)']

    if attributes is None:
        attributes = 'cn', 'sudoCommand'

    if 'cn' in params:
        condition_list.append('(cn=%s)' % escape_filter_chars(params['cn']))
    if 'cnlike' in params:
        condition_list.append('(cn=*%s*)' % escape_filter_chars(params['cnlike']))
    if 'cnin' in params:
        _cns = []
        for cn in params['cnin']:
            _cns.append('(cn=%s)' % escape_filter_chars(cn))
        condition_list.append('(|%s)' % ''.join(_cns))

    condition_str = '(&' + ''.join(condition_list) + ')'
    return g.openldap_session.search_commands(condition_str, attributes)


def list_commands(key='cn'):
    return list(map(lambda x: x[key], search_commands([key])))


def get_command(cn):
    commands = search_commands(cn=cn)
    return commands[0] if len(commands) > 0 else None


@openldap_session
def add_command(cn, sudo_command=None):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.add_command(cn, sudo_command=sudo_command)


@openldap_session
def modify_command(cn, **other_attrs):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.modify_command(cn, **other_attrs)


@openldap_session
def delete_command(cn):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.delete_command(cn)


@openldap_session
def search_command_groups(attributes=None, **params):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    condition_list = ['(objectClass=*)', '(objectClass=groupOfUniqueNames)']

    if attributes is None:
        attributes = 'cn', 'uniqueMember'

    if 'cn' in params:
        condition_list.append('(cn=%s)' % escape_filter_chars(params['cn']))
    if 'cnlike' in params:
        condition_list.append('(cn=*%s*)' % escape_filter_chars(params['cnlike']))
    if 'unique_member' in params:
        condition_list.append('(uniqueMember=%s)' % g.openldap_session.assemble_command_dn(escape_filter_chars(params['unique_member'])))

    condition_str = '(&' + ''.join(condition_list) + ')'
    results = g.openldap_session.search_command_groups(condition_str, attributes)
    for result in results:
        if 'uniqueMember' in result:
            result['uniqueMember'] = list(map(g.openldap_session.extract_cn, result['uniqueMember']))
    return results


def list_command_groups(key='cn'):
    return list(map(lambda x: x[key], search_command_groups([key])))


def get_command_group(cn):
    command_groups = search_command_groups(cn=cn)
    return command_groups[0] if len(command_groups) > 0 else None


@openldap_session
def add_command_group(cn):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.add_command_group(cn)


@openldap_session
def modify_command_group(cn, unique_member=None):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.modify_command_group(cn, unique_member)


@openldap_session
def delete_command_group(cn):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.delete_command_group(cn)


@openldap_session
def search_services(attributes=None, **params):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    condition_list = ['(objectClass=*)', '(objectClass=authorizedServiceObject)']

    if attributes is None:
        attributes = 'cn', 'authorizedService'

    if 'cn' in params:
        condition_list.append('(cn=%s)' % escape_filter_chars(params['cn']))
    if 'cnlike' in params:
        condition_list.append('(cn=*%s*)' % escape_filter_chars(params['cnlike']))
    if 'cnin' in params:
        _cns = []
        for cn in params['cnin']:
            _cns.append('(cn=%s)' % escape_filter_chars(cn))
        condition_list.append('(|%s)' % ''.join(_cns))

    condition_str = '(&' + ''.join(condition_list) + ')'
    return g.openldap_session.search_services(condition_str, attributes)


def list_services(key='cn'):
    return list(map(lambda x: x[key], search_services([key])))


def list_all_servicepoints():
    services = set()
    for s in search_services():
        services.update(s['authorizedService'])
    return list(services)


def get_service(cn):
    services = search_services(cn=cn)
    return services[0] if len(services) > 0 else None


@openldap_session
def add_service(cn, authorized_service=None):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.add_service(cn, authorized_service=authorized_service)


@openldap_session
def modify_service(cn, **other_attrs):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.modify_service(cn, **other_attrs)


@openldap_session
def delete_service(cn):
    assert isinstance(g.openldap_session, OpenLDAPSession)
    return g.openldap_session.delete_service(cn)


def _rebuild_user_auth(auth):
    attrs = {
        'update_host': objects.contains(auth['sourceentity'], ENTITY_HOST, ENTITY_HOSTGROUP),
        'update_command': objects.contains(auth['sourceentity'], ENTITY_COMMAND, ENTITY_COMMANDGROUP),
        'update_service': objects.contains(auth['sourceentity'], ENTITY_SERVICE, ENTITY_SERVICEPOINT),
    }
    if auth['grantentity'] == ENTITY_USER:
        update_users_auth_attr(auth['grantid'], **attrs)
    elif auth['grantentity'] == ENTITY_GROUP:
        update_group_auth_attr(auth['grantid'], **attrs)


def save_auth(auth):
    um_models.save_auth(auth)
    _rebuild_user_auth(auth)


def delete_auth(auth):
    um_models.delete_auth(auth['id'])
    _rebuild_user_auth(auth)


@openldap_session
def update_users_auth_attr(*cn_list, update_host=False, update_command=False, update_service=False):
    def group_members(group_cn, _users, _groups):
        gid = None
        group = None
        for _group in _groups:
            if _group['cn'] == group_cn:
                try:
                    return _group['members']
                except KeyError:
                    pass
                group = _group
                gid = _group['gidNumber']
                break
        if gid is None:
            raise Exception('Unexpected error')
        results = []
        for _user in _users:
            if str(_user['gidNumber']) == str(gid):
                results.append(_user['cn'])
        group['member'] = results
        return results

    assert isinstance(g.openldap_session, OpenLDAPSession)

    if len(cn_list) == 0:
        return

    # decide sourceentityin
    if not (update_host or update_command or update_service):
        return
    sourceentityin = []
    if update_host:
        sourceentityin.append(ENTITY_HOST)
        sourceentityin.append(ENTITY_HOSTGROUP)
    if update_command:
        sourceentityin.append(ENTITY_COMMAND)
        sourceentityin.append(ENTITY_COMMANDGROUP)
    if update_service:
        sourceentityin.append(ENTITY_SERVICE)
        sourceentityin.append(ENTITY_SERVICEPOINT)

    # get the groups which the users belong to
    users = search_users(attributes=['cn', 'gidNumber'], cnin=cn_list)
    gid_number_list = list(map(lambda x: x['gidNumber'], users))
    groups = search_groups(attributes=['cn', 'gidNumber'], gid_number_in=gid_number_list)
    group_cn_list = list(map(lambda x: x['cn'], groups))

    # init user changes object
    user_changes = {}
    _all_commands = None
    _all_services = None
    _service_dict = {}
    for cn in cn_list:
        user_changes[cn] = {}
        if update_host:
            user_changes[cn]['host'] = set()
        if update_command:
            user_changes[cn]['sudoCommand'] = set()
            _all_commands = set()
        if update_service:
            user_changes[cn]['authorizedService'] = set()
            _all_services = set()
            _service_dict[cn] = set()

    # get all authenticated hosts, commands, services
    auth_list = um_models.find_auth(grantentity=ENTITY_USER, grantidin=cn_list, sourceentityin=sourceentityin).fetch()
    if len(groups) > 0:
        auth_list.extend(um_models.find_auth(grantentity=ENTITY_GROUP, grantidin=group_cn_list, sourceentityin=sourceentityin).fetch())
    for auth in auth_list:
        sourceentity = auth['sourceentity']
        sourceid = auth['sourceid']
        grantentity = auth['grantentity']
        grantid = auth['grantid']

        if sourceentity == ENTITY_HOST:
            if grantentity == ENTITY_USER:
                user_changes[grantid]['host'].add(sourceid)
            elif grantentity == ENTITY_GROUP:
                for member in group_members(grantid, users, groups):
                    user_changes[member]['host'].add(sourceid)
        elif sourceentity == ENTITY_HOSTGROUP:
            host_group = get_host_group(sourceid)
            if host_group is not None:
                if grantentity == ENTITY_USER:
                    user_changes[grantid]['host'].update(host_group['uniqueMember'])
                elif grantentity == ENTITY_GROUP:
                    for member in group_members(grantid, users, groups):
                        user_changes[member]['host'].update(host_group['uniqueMember'])
        elif sourceentity == ENTITY_COMMAND:
            _all_commands.add(sourceid)
            if grantentity == ENTITY_USER:
                user_changes[grantid]['sudoCommand'].add(sourceid) # fake, for cache reason
            elif grantentity == ENTITY_GROUP:
                for member in group_members(grantid, users, groups):
                    user_changes[member]['sudoCommand'].add(sourceid)
        elif sourceentity == ENTITY_COMMANDGROUP:
            command_group = get_command_group(sourceid)
            if command_group is not None:
                _all_commands.update(command_group['uniqueMember'])
                if grantentity == ENTITY_USER:
                    user_changes[grantid]['sudoCommand'].update(command_group['uniqueMember'])
                elif grantentity == ENTITY_GROUP:
                    for member in group_members(grantid, users, groups):
                        user_changes[member]['sudoCommand'].update(command_group['uniqueMember'])
        elif sourceentity == ENTITY_SERVICE:
            _all_services.add(sourceid)
            if grantentity == ENTITY_USER:
                _service_dict[grantid].add(sourceid)
            elif grantentity == ENTITY_GROUP:
                for member in group_members(grantid, users, groups):
                    _service_dict[member].add(sourceid)
        elif sourceentity == ENTITY_SERVICEPOINT:
            if grantentity == ENTITY_USER:
                user_changes[grantid]['authorizedService'].add(sourceid)
            elif grantentity == ENTITY_GROUP:
                for member in group_members(grantid, users, groups):
                    user_changes[member]['authorizedService'].add(sourceid)

    # process command
    if update_command and len(_all_commands) > 0:
        command_dict = {}
        for i in search_commands(cnin=_all_commands):
            command_dict[i['cn']] = i['sudoCommand']
        for cn, changes in user_changes.items():
            sudo_command = set()
            for _cmd_cn in changes['sudoCommand']:
                sudo_command.update(command_dict[_cmd_cn])
            changes['sudoCommand'] = sudo_command

    # process service
    if update_service and len(_all_services) > 0:
        service_dict = {}
        for i in search_services(cnin=_all_services):
            service_dict[i['cn']] = i['authorizedService']
        for cn, services in _service_dict.items():
            for service in services:
                user_changes[cn]['authorizedService'].update(service_dict[service])

    # finally update the user
    for cn, changes in user_changes.items():
        g.openldap_session.modify_user(cn, skip_event_callback=True, **changes)

def update_group_auth_attr(group_cn, update_host=False, update_command=False, update_service=False):
    group_members = search_users(attributes=['cn'], group=group_cn)
    user_cn_list = set(map(lambda x: x['cn'], group_members))
    update_users_auth_attr(*user_cn_list, update_host=update_host, update_command=update_command, update_service=update_service)
