# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import collections
import copy
from datetime import datetime, timedelta

import six
from ldap3 import Server, Connection, NONE, HASHED_SALTED_SHA, MODIFY_REPLACE, MODIFY_DELETE, ALL_ATTRIBUTES, SUBTREE, BASE, AUTO_BIND_TLS_BEFORE_BIND
from ldap3.utils.hashed import hashed
from ldap3.utils.log import set_library_log_detail_level, BASIC

from raphael.utils import strings, num, objects, inflection, logger, time

LOGGER_NAME = 'OPENLDAP'
set_library_log_detail_level(BASIC)


class OpenLDAPSession(object):
    __slots__ = ['uri', 'basedn', 'manager', 'passwd', 'ou_people', 'ou_groups', 'ou_hosts', 'ou_host_groups',
                 'ou_commands', 'ou_command_groups', 'ou_services', 'server', 'connection', 'event_handlers']

    EVENT_ON_USER_CREATED = 'on_user_created'
    EVENT_ON_USER_MODIFIED = 'on_user_modified'
    EVENT_ON_USER_DELETED = 'on_user_deleted'
    EVENT_ON_GROUP_CREATED = 'on_group_created'
    EVENT_ON_GROUP_MODIFIED = 'on_group_modified'
    EVENT_ON_GROUP_DELETED = 'on_group_deleted'
    EVENT_ON_HOST_CREATED = 'on_host_created'
    EVENT_ON_HOST_MODIFIED = 'on_host_modified'
    EVENT_ON_HOST_DELETED = 'on_host_deleted'
    EVENT_ON_HOSTGROUP_CREATED = 'on_hostgroup_created'
    EVENT_ON_HOSTGROUP_MODIFIED = 'on_hostgroup_modified'
    EVENT_ON_HOSTGROUP_DELETED = 'on_hostgroup_deleted'
    EVENT_ON_COMMAND_CREATED = 'on_command_created'
    EVENT_ON_COMMAND_MODIFIED = 'on_command_modified'
    EVENT_ON_COMMAND_DELETED = 'on_command_deleted'
    EVENT_ON_COMMANDGROUP_CREATED = 'on_commandgroup_created'
    EVENT_ON_COMMANDGROUP_MODIFIED = 'on_commandgroup_modified'
    EVENT_ON_COMMANDGROUP_DELETED = 'on_commandgroup_deleted'
    EVENT_ON_SERVICE_CREATED = 'on_service_created'
    EVENT_ON_SERVICE_MODIFIED = 'on_service_modified'
    EVENT_ON_SERVICE_DELETED = 'on_service_deleted'

    def __init__(self, uri, basedn, manager, passwd, start_tls=False, ou_people='people', ou_groups='groups', ou_hosts='hosts',
                 ou_host_groups='hostGroups', ou_commands='commands', ou_command_groups='commandGroups', ou_services='services',
                 event_handlers=None):
        self.uri = uri
        self.basedn = basedn
        self.manager = manager
        self.passwd = passwd
        self.ou_people = ou_people
        self.ou_groups = ou_groups
        self.ou_hosts = ou_hosts
        self.ou_host_groups = ou_host_groups
        self.ou_commands = ou_commands
        self.ou_command_groups = ou_command_groups
        self.ou_services = ou_services

        self.server = Server(self.uri, get_info=NONE)
        self.connection = Connection(self.server, user=self.manager, password=self.passwd, auto_bind=AUTO_BIND_TLS_BEFORE_BIND if start_tls else True)

        self.event_handlers = event_handlers
        if self.event_handlers is not None:
            for handler in self.event_handlers:
                handler.session = self

    def __enter__(self):
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.__exit__(exc_type, exc_val, exc_tb)

    @property
    def _placeholder(self):
        return 'cn=null,' + self.basedn

    @staticmethod
    def _get_entry_value(entry, key):
        if not hasattr(entry, key):
            return None
        return entry[key].value

    @staticmethod
    def _epoch_days():
        """
        days from 1970-01-01
        :return: int
        """
        return (time.utcnow() - datetime(1970, 1, 1)).days

    @staticmethod
    def _get_date_from_epoch_days(epoch):
        """
        get date from epoch days
        :param epoch: epoch days
        :return:
        """
        return (datetime(1970, 1, 1) + timedelta(days=epoch)).date()

    def _event_handler(self, event, *args, **kwargs):
        if self.event_handlers is not None:
            for event_handler in self.event_handlers:
                try:
                    getattr(event_handler, event)(*args, **kwargs)
                except:
                    logger.error_traceback(LOGGER_NAME)

    def construct_skeleton(self):
        """
        Build OpenLDAP skeleton
        :return:
        """
        for ou in self.ou_people, self.ou_groups, self.ou_hosts, self.ou_host_groups, self.ou_commands, self.ou_command_groups, self.ou_services:
            if not self.connection.search(self.basedn, '(ou=%s)' % ou):
                self.connection.add(','.join(('ou=' + ou, self.basedn)), ['organizationalUnit'], {'ou': ou})

    def assemble_dn(self, cn, ou):
        return ','.join(('cn=' + cn, 'ou=' + ou, self.basedn))

    def assemble_user_dn(self, cn):
        return self.assemble_dn(cn, self.ou_people)

    def assemble_group_dn(self, cn):
        return self.assemble_dn(cn, self.ou_groups)

    def assemble_host_dn(self, cn):
        return self.assemble_dn(cn, self.ou_hosts)

    def assemble_host_group_dn(self, cn):
        return self.assemble_dn(cn, self.ou_host_groups)

    def assemble_command_dn(self, cn):
        return self.assemble_dn(cn, self.ou_commands)

    def assemble_command_group_dn(self, cn):
        return self.assemble_dn(cn, self.ou_command_groups)

    def assemble_service_dn(self, cn):
        return self.assemble_dn(cn, self.ou_services)

    @staticmethod
    def extract_cn(dn):
        return dn.split(',')[0].split('=')[1]

    def search(self, search_base, search_filter, search_scope=SUBTREE, attributes=None):
        return self.connection.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=search_scope,
            attributes=attributes,
        ), self.connection.entries

    def search_common(self, search_base, search_filter, search_scope=SUBTREE, attributes=None):
        success, entries = self.search(search_base, search_filter, search_scope=search_scope, attributes=attributes)
        ret = []
        if success:
            for entry in entries:
                obj = {'dn': entry.entry_dn}
                for k, v in entry.__dict__.items():
                    try:
                        obj[k] = v.value
                    except AttributeError:
                        pass
                ret.append(obj)
        return ret

    def search_users(self, search_filter, attributes=None):
        return self.search_common(','.join(('ou=' + self.ou_people, self.basedn)), search_filter, attributes=attributes)

    def search_groups(self, search_filter, attributes=None):
        return self.search_common(','.join(('ou=' + self.ou_groups, self.basedn)), search_filter, attributes=attributes)

    def search_hosts(self, search_filter, attributes=None):
        return self.search_common(','.join(('ou=' + self.ou_hosts, self.basedn)), search_filter, attributes=attributes)

    def search_host_groups(self, search_filter, attributes=None):
        results = self.search_common(','.join(('ou=' + self.ou_host_groups, self.basedn)), search_filter, attributes=attributes)
        if 'uniqueMember' in attributes:
            for result in results:
                if isinstance(result['uniqueMember'], six.string_types):
                    if result['uniqueMember'] == self._placeholder:
                        result['uniqueMember'] = []
                    else:
                        result['uniqueMember'] = [result['uniqueMember']]
                elif isinstance(result['uniqueMember'], collections.Iterable):
                    result['uniqueMember'] = list(filter(lambda x: x != self._placeholder, result['uniqueMember']))
        return results

    def search_commands(self, search_filter, attributes=None):
        results = self.search_common(','.join(('ou=' + self.ou_commands, self.basedn)), search_filter, attributes=attributes)
        if 'sudoCommand' in attributes:
            for result in results:
                if isinstance(result['sudoCommand'], six.string_types):
                    result['sudoCommand'] = [result['sudoCommand']]
        return results

    def search_command_groups(self, search_filter, attributes=None):
        results = self.search_common(','.join(('ou=' + self.ou_command_groups, self.basedn)), search_filter, attributes=attributes)
        if 'uniqueMember' in attributes:
            for result in results:
                if isinstance(result['uniqueMember'], six.string_types):
                    if result['uniqueMember'] == self._placeholder:
                        result['uniqueMember'] = []
                    else:
                        result['uniqueMember'] = [result['uniqueMember']]
                elif isinstance(result['uniqueMember'], collections.Iterable):
                    result['uniqueMember'] = list(filter(lambda x: x != self._placeholder, result['uniqueMember']))
        return results

    def search_services(self, search_filter, attributes=None):
        results = self.search_common(','.join(('ou=' + self.ou_services, self.basedn)), search_filter, attributes=attributes)
        if 'authorizedService' in attributes:
            for result in results:
                if isinstance(result['authorizedService'], six.string_types):
                    result['authorizedService'] = [result['authorizedService']]
        return results

    def get(self, dn, attributes=None):
        objs = self.search_common(dn, '(objectClass=*)', search_scope=BASE, attributes=attributes)
        return objs[0] if len(objs) > 0 else None

    def get_user(self, cn, attributes=None):
        users = self.search_users(search_filter='(&(objectClass=person)(cn=%s))' % cn, attributes=attributes)
        return users[0] if len(users) > 0 else None

    def get_group(self, cn, attributes=None):
        groups = self.search_groups(search_filter='(&(objectClass=posixGroup)(cn=%s))' % cn, attributes=attributes)
        return groups[0] if len(groups) > 0 else None

    def get_host(self, cn, attributes=None):
        hosts = self.search_hosts(search_filter='(&(objectClass=device)(cn=%s))' % cn, attributes=attributes)
        return hosts[0] if len(hosts) > 0 else None

    def get_host_group(self, cn, attributes=None):
        host_groups = self.search_host_groups(search_filter='(&(objectClass=groupOfUniqueNames)(cn=%s))' % cn, attributes=attributes)
        return host_groups[0] if len(host_groups) > 0 else None

    def get_command(self, cn, attributes=None):
        commands = self.search_commands(search_filter='(&(objectClass=sudoRole)(cn=%s))' % cn, attributes=attributes)
        return commands[0] if len(commands) > 0 else None

    def get_command_group(self, cn, attributes=None):
        command_groups = self.search_command_groups(search_filter='(&(objectClass=groupOfUniqueNames)(cn=%s))' % cn, attributes=attributes)
        return command_groups[0] if len(command_groups) > 0 else None

    def get_service(self, cn, attributes=None):
        services = self.search_services(search_filter='(&(objectClass=authorizedServiceObject)(cn=%s))' % cn, attributes=attributes)
        return services[0] if len(services) > 0 else None

    def add(self, dn, object_class=None, attributes=None, controls=None, event=None, skip_event_callback=False):
        result = self.connection.add(dn, object_class=object_class, attributes=attributes, controls=controls)
        if not skip_event_callback:
            self._event_handler(event, dn, object_class=object_class, attributes=attributes)
        return result

    def add_user(self, cn, sn, uid_number, gid_number=100, gecos=None, mail=None, display_name=None,
                 shadow_min=None, shadow_max=None, shadow_inactive=None, shadow_warning=None, shadow_last_change=None,
                 skip_event_callback=False):
        # check value
        if strings.is_blank(cn):
            raise Exception('cn cannot be blank')
        if strings.is_blank(sn):
            raise Exception('sn cannot be blank')
        if num.safe_int(uid_number) <= 1000:
            raise Exception('uidNumber should > 1000')

        attributes = {
            'cn': cn,
            'uid': cn,
            'sn': sn,
            'uidNumber': num.safe_int(uid_number),
            'gidNumber': num.safe_int(gid_number),
            'homeDirectory': '/home/' + cn,
            'loginShell': '/bin/bash',
            'userPassword': '{crypt}x',
            'sudoUser': cn,
            'sudoHost': 'ALL',
            'sudoOption': '!authenticate',
        }
        if gecos is not None:
            attributes['gecos'] = gecos
        if mail is not None:
            attributes['mail'] = mail
        if display_name is not None:
            attributes['displayName'] = display_name
        if shadow_min is not None:
            attributes['shadowMin'] = shadow_min
        if shadow_max is not None:
            attributes['shadowMax'] = shadow_max
        if shadow_inactive is not None:
            attributes['shadowInactive'] = shadow_inactive
        if shadow_warning is not None:
            attributes['shadowWarning'] = shadow_warning
        if shadow_last_change is not None:
            attributes['shadowLastChange'] = shadow_last_change  # set 0 to force change password on the first login
        else:
            attributes['shadowLastChange'] = self._epoch_days()

        return self.add(
            dn=self.assemble_user_dn(cn),
            object_class=['top', 'posixAccount', 'shadowAccount', 'person', 'inetOrgPerson', 'hostObject', 'sudoRole', 'authorizedServiceObject'],
            attributes=attributes,
            event=self.EVENT_ON_USER_CREATED,
            skip_event_callback=skip_event_callback,
        )

    def add_group(self, cn, gid_number, skip_event_callback=False):
        return self.add(
            dn=self.assemble_group_dn(cn),
            object_class=['top', 'posixGroup'],
            attributes={
                'gidNumber': gid_number
            },
            event=self.EVENT_ON_GROUP_CREATED,
            skip_event_callback=skip_event_callback,
        )

    def add_host(self, cn, cn_list=None, ip_host_number=None, skip_event_callback=False):
        attributes = {}
        if strings.is_blank(cn):
            raise Exception("host cn can't be blank")
        if cn_list is not None and not isinstance(cn_list, collections.Iterable):
            raise Exception("host cn_list should be iterable or None")
        cn_list = set(cn_list).add(cn)
        attributes['cn'] = cn if cn_list is None else cn_list
        if ip_host_number is not None:
            attributes['ipHostNumber'] = ip_host_number
        return self.add(
            dn=self.assemble_host_dn(cn),
            object_class=['top', 'device', 'ipHost'],
            attributes=attributes,
            event=self.EVENT_ON_HOST_CREATED,
            skip_event_callback=skip_event_callback,
        )

    def add_host_group(self, cn, skip_event_callback=False):
        return self.add(
            dn=self.assemble_host_group_dn(cn),
            object_class=['top', 'groupOfUniqueNames'],
            attributes={
                'cn': cn,
                'uniqueMember': [self._placeholder],
            },
            event=self.EVENT_ON_HOSTGROUP_CREATED,
            skip_event_callback=skip_event_callback,
        )

    def add_command(self, cn, sudo_command=None, skip_event_callback=False):
        attributes = {
            'cn': cn,
            'sn': cn,
        }
        if sudo_command is not None:
            attributes['sudoCommand'] = sudo_command
        return self.add(
            dn=self.assemble_command_dn(cn),
            object_class=['top', 'person', 'sudoRole'],
            attributes=attributes,
            event=self.EVENT_ON_COMMAND_CREATED,
            skip_event_callback=skip_event_callback,
        )

    def add_command_group(self, cn, skip_event_callback=False):
        return self.add(
            dn=self.assemble_command_group_dn(cn),
            object_class=['top', 'groupOfUniqueNames'],
            attributes={
                'cn': cn,
                'uniqueMember': [self._placeholder],
            },
            event=self.EVENT_ON_COMMANDGROUP_CREATED,
            skip_event_callback=skip_event_callback,
        )

    def add_service(self, cn, authorized_service=None, skip_event_callback=False):
        attributes = {
            'cn': cn,
            'sn': cn,
        }
        if authorized_service is not None:
            attributes['authorizedService'] = authorized_service
        return self.add(
            dn=self.assemble_service_dn(cn),
            object_class=['top', 'person', 'authorizedServiceObject'],
            attributes=attributes,
            event=self.EVENT_ON_SERVICE_CREATED,
            skip_event_callback=skip_event_callback,
        )

    @staticmethod
    def _make_changes(legal_attrs, **other_attrs):
        changes = {}
        for attribute, v in other_attrs.items():
            if not objects.contains(attribute, *legal_attrs):
                raise Exception('illegal attribute in "other_attrs": %s' % attribute)
            if v is None:
                changes[inflection.camelize(attribute, False)] = MODIFY_DELETE, []
            else:
                if isinstance(v, six.string_types):
                    changes[inflection.camelize(attribute, False)] = MODIFY_REPLACE, [v]
                elif isinstance(v, collections.Iterable):
                    changes[inflection.camelize(attribute, False)] = MODIFY_REPLACE, v
                else:
                    raise Exception('illegal type found for "%s"' % attribute)
        return changes

    def modify(self, dn, changes, controls=None, event=None, skip_event_callback=False):
        has_event = self.event_handlers is not None and event is not None and not skip_event_callback
        oldobject = None
        if has_event:
            oldobject = self.get(dn, ALL_ATTRIBUTES)
        result = self.connection.modify(dn, changes, controls=controls)
        if has_event:
            self._event_handler(event, dn, changes, oldobject=oldobject)
        return result

    def modify_user(self, cn, sn=None, uid_number=None, skip_event_callback=False, **other_attrs):
        changes = {}
        legal_attrs = ('gid_number', 'gecos', 'mail', 'display_name', 'shadow_min', 'shadow_max', 'shadow_inactive', 'shadow_warning', 'host', 'sudoCommand', 'authorizedService')
        if sn is not None:
            changes['sn'] = MODIFY_REPLACE, [sn]
        if uid_number is not None:
            changes['uidNumber'] = MODIFY_REPLACE, [uid_number]
        changes.update(self._make_changes(legal_attrs, **other_attrs))
        return self.modify(self.assemble_user_dn(cn), changes, event=self.EVENT_ON_USER_MODIFIED, skip_event_callback=skip_event_callback)

    def modify_group(self, cn, gid_number=None, skip_event_callback=False, **other_attrs):
        changes = {}
        legal_attrs = ('memberUid', 'description')
        if gid_number is not None:
            changes['gidNumber'] = MODIFY_REPLACE, [gid_number]
        changes.update(self._make_changes(legal_attrs, **other_attrs))
        return self.modify(self.assemble_group_dn(cn), changes, event=self.EVENT_ON_GROUP_MODIFIED, skip_event_callback=skip_event_callback)

    def modify_host(self, cn, skip_event_callback=False, **other_attrs):
        changes = {}
        cn_list = other_attrs.get('cn_list')
        if cn_list is not None:
            if not isinstance(cn_list, collections.Iterable):
                raise Exception("host cn_list should be iterable or None")
            cn_list = set(cn_list).add(cn)
            changes['cn'] = MODIFY_REPLACE, cn_list
        legal_attrs = ['ip_host_number']
        new_other_attrs = copy.deepcopy(other_attrs)
        if hasattr(new_other_attrs, 'cn_list'):
            del new_other_attrs['cn_list']
        changes.update(self._make_changes(legal_attrs, **new_other_attrs))
        return self.modify(self.assemble_host_dn(cn), changes, event=self.EVENT_ON_HOST_MODIFIED, skip_event_callback=skip_event_callback)

    def modify_host_group(self, cn, unique_member=None, skip_event_callback=False):
        changes = {}
        if unique_member is not None:
            if not (isinstance(unique_member, collections.Iterable) and isinstance(unique_member, collections.Sized)):
                raise Exception("host group unique_member should be iterable or None")
            if len(unique_member) == 0:
                changes['uniqueMember'] = MODIFY_REPLACE, [self._placeholder]
            else:
                changes['uniqueMember'] = MODIFY_REPLACE, list(map(lambda x: self.assemble_host_dn(x), unique_member))
            return self.modify(self.assemble_host_group_dn(cn), changes, event=self.EVENT_ON_HOSTGROUP_MODIFIED, skip_event_callback=skip_event_callback)

    def modify_command(self, cn, skip_event_callback=False, **other_attrs):
        return self.modify(
            self.assemble_command_dn(cn),
            self._make_changes(['sudoCommand'], **other_attrs),
            event=self.EVENT_ON_COMMAND_MODIFIED,
            skip_event_callback=skip_event_callback
        )

    def modify_command_group(self, cn, unique_member=None, skip_event_callback=False):
        changes = {}
        if unique_member is not None:
            if not (isinstance(unique_member, collections.Iterable) and isinstance(unique_member, collections.Sized)):
                raise Exception("command group unique_member should be iterable or None")
            if len(unique_member) == 0:
                changes['uniqueMember'] = MODIFY_REPLACE, [self._placeholder]
            else:
                changes['uniqueMember'] = MODIFY_REPLACE, list(map(lambda x: self.assemble_command_dn(x), unique_member))
            return self.modify(self.assemble_command_group_dn(cn), changes, event=self.EVENT_ON_COMMANDGROUP_MODIFIED, skip_event_callback=skip_event_callback)

    def modify_service(self, cn, skip_event_callback=False, **other_attrs):
        return self.modify(
            self.assemble_service_dn(cn),
            self._make_changes(['authorizedService'], **other_attrs),
            event=self.EVENT_ON_SERVICE_MODIFIED,
            skip_event_callback=skip_event_callback
        )

    def delete(self, dn, controls=None, event=None, skip_event_callback=False):
        has_event = self.event_handlers is not None and event is not None and not skip_event_callback
        oldobject = None
        if has_event:
            oldobject = self.get(dn, ALL_ATTRIBUTES)
        result = self.connection.delete(dn, controls=controls)
        if has_event:
            self._event_handler(event, dn, oldobject=oldobject)
        return result

    def delete_user(self, cn, skip_event_callback=False):
        return self.delete(self.assemble_user_dn(cn), event=self.EVENT_ON_USER_DELETED, skip_event_callback=skip_event_callback)

    def delete_group(self, cn, skip_event_callback=False):
        return self.delete(self.assemble_group_dn(cn), event=self.EVENT_ON_GROUP_DELETED, skip_event_callback=skip_event_callback)

    def delete_host(self, cn, skip_event_callback=False):
        dn = self.assemble_host_dn(cn)
        result = self.delete(dn, event=self.EVENT_ON_HOST_DELETED, skip_event_callback=skip_event_callback)
        host_groups = self.search_host_groups('(uniqueMember=%s)' % self.assemble_host_dn(cn), attributes=['cn', 'uniqueMember'])
        for host_group in host_groups:
            _cn = host_group.get('cn')
            host_group.get('uniqueMember').remove(dn)
            self.modify_host_group(_cn, list(map(lambda x: self.extract_cn(x), host_group.get('uniqueMember'))), skip_event_callback=True)
        return  result

    def delete_host_group(self, cn, skip_event_callback=False):
        return self.delete(self.assemble_host_group_dn(cn), event=self.EVENT_ON_HOSTGROUP_DELETED, skip_event_callback=skip_event_callback)

    def delete_command(self, cn, skip_event_callback=False):
        dn = self.assemble_command_dn(cn)
        result = self.delete(dn, event=self.EVENT_ON_COMMAND_DELETED, skip_event_callback=skip_event_callback)
        command_groups = self.search_command_groups('(uniqueMember=%s)' % self.assemble_command_dn(cn), attributes=['cn', 'uniqueMember'])
        for command_group in command_groups:
            _cn = command_group.get('cn')
            command_group.get('uniqueMember').remove(dn)
            self.modify_command_group(_cn, list(map(lambda x: self.extract_cn(x), command_group.get('uniqueMember'))))
        return result

    def delete_command_group(self, cn, skip_event_callback=False):
        return self.delete(self.assemble_command_group_dn(cn), event=self.EVENT_ON_COMMANDGROUP_DELETED, skip_event_callback=skip_event_callback)

    def delete_service(self, cn, skip_event_callback=False):
        return self.delete(self.assemble_service_dn(cn), event=self.EVENT_ON_SERVICE_DELETED, skip_event_callback=skip_event_callback)

    def reset_password(self, cn, new_password=None, shadow_last_change=None):
        hashed_password = hashed(HASHED_SALTED_SHA, new_password)
        self.connection.modify(
            self.assemble_user_dn(cn),
            {
                'userPassword': [(MODIFY_REPLACE, [hashed_password])],
                'shadowLastChange': [(MODIFY_REPLACE, shadow_last_change if shadow_last_change is not None else self._epoch_days())],
            }
        )


class OpenLDAPEvents(object):
    def __init__(self):
        self.session = None

    def on_user_created(self, dn, object_class=None, attributes=None):
        raise NotImplementedError()

    def on_user_modified(self, dn, changes, oldobject):
        raise NotImplementedError()

    def on_user_deleted(self, dn, oldobject):
        raise NotImplementedError()

    def on_group_created(self, dn, object_class=None, attributes=None):
        raise NotImplementedError()

    def on_group_modified(self, dn, changes, oldobject):
        raise NotImplementedError()

    def on_group_deleted(self, dn, oldobject):
        raise NotImplementedError()

    def on_host_created(self, dn, object_class=None, attributes=None):
        raise NotImplementedError()

    def on_host_modified(self, dn, changes, oldobject):
        raise NotImplementedError()

    def on_host_deleted(self, dn, oldobject):
        raise NotImplementedError()

    def on_hostgroup_created(self, dn, object_class=None, attributes=None):
        raise NotImplementedError()

    def on_hostgroup_modified(self, dn, changes, oldobject):
        raise NotImplementedError()

    def on_hostgroup_deleted(self, dn, oldobject):
        raise NotImplementedError()

    def on_command_created(self, dn, object_class=None, attributes=None):
        raise NotImplementedError()

    def on_command_modified(self, dn, changes, oldobject):
        raise NotImplementedError()

    def on_command_deleted(self, dn, oldobject):
        raise NotImplementedError()

    def on_commandgroup_created(self, dn, object_class=None, attributes=None):
        raise NotImplementedError()

    def on_commandgroup_modified(self, dn, changes, oldobject):
        raise NotImplementedError()

    def on_commandgroup_deleted(self, dn, oldobject):
        raise NotImplementedError()

    def on_service_created(self, dn, object_class=None, attributes=None):
        raise NotImplementedError()

    def on_service_modified(self, dn, changes, oldobject):
        raise NotImplementedError()

    def on_service_deleted(self, dn, oldobject):
        raise NotImplementedError()
