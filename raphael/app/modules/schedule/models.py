# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import json
from apscheduler.jobstores.base import JobLookupError
from raphael.utils.dao.context import DBContext
from raphael.utils import num, strings, time, task, logger

TASK_DATABASE = 'database'


def get_schedule(oid):
    ctx = DBContext()
    return ctx.get('cm_schedule', oid)


def save_task_schedule(o):
    if strings.is_blank(o.get('id', None)):
        raise ValueError('Field "id" not in this object: ' + str(o))
    if o['enabled']:
        # prepare args & kwargs
        args = None
        kwargs = None
        try:
            args_kwargs = json.loads(o['args'])
            args = args_kwargs['args']
            kwargs = args_kwargs['kwargs']
        except:
            pass
        # add
        if o['type'] == 1:  # date
            task.add_date_job(o['func'], o['id'], TASK_DATABASE, args=args, kwargs=kwargs, run_date=time.string_to_date(o['data'], '%Y-%m-%d %H:%M:%S'), timezone='utc')
        elif o['type'] == 2:  # interval
            interval = json.loads(o['data'])
            task.add_interval_job(o['func'], o['id'], TASK_DATABASE, args=args, kwargs=kwargs, weeks=num.safe_int(interval['weeks']), days=num.safe_int(interval['days']),
                                  hours=num.safe_int(interval['hours']), minutes=num.safe_int(interval['minutes']), seconds=num.safe_int(interval['seconds']),
                                  start_date=o['starttime'], end_date=o['endtime'], timezone='utc')
        elif o['type'] == 3:  # cron
            cron = json.loads(o['data'])
            task.add_cron_job(o['func'], o['id'], TASK_DATABASE, args=args, kwargs=kwargs, year=cron['year'], month=cron['month'], day=cron['day'],
                              day_of_week=cron['day_of_week'], hour=cron['hour'], minute=cron['minute'], second=cron['second'],
                              start_date=o['starttime'], end_date=o['endtime'], timezone='utc')
    else:
        try:
            task.remove_job(o['id'], TASK_DATABASE)
        except JobLookupError:
            pass


def save_schedule(o):
    with DBContext() as ctx:
        ctx.save('cm_schedule', o)


def save_schedule_manually(o):
    with DBContext():
        save_schedule(o)
        save_task_schedule(o)


def delete_schedule(oid):
    with DBContext() as ctx:
        ctx.delete_byid('cm_schedule', oid)
        ctx.execute_delete('cm_schedule_log', 'scheduleid = :sid', sid=oid)
        try:
            task.remove_job(oid, TASK_DATABASE)
        except JobLookupError:
            logger.error_traceback()


def find_schedules(**params):
    ctx = DBContext()
    sql = ['1=1']
    cond = {}
    if 'enabled' in params:
        sql.append('and enabled = :enabled')
        cond['enabled'] = params['enabled']
    if 'type' in params:
        sql.append('and type = :type')
        cond['type'] = params['type']
    if 'module' in params:
        sql.append('and module = :module')
        cond['module'] = params['module']
    if 'modulelike' in params:
        sql.append('and module like :modulelike')
        cond['modulelike'] = '%' + params['modulelike'] + '%'
    if 'sourceid' in params:
        sql.append('and sourceid = :sourceid')
        cond['sourceid'] = params['sourceid']
    return ctx.create_query('cm_schedule', ' '.join(sql), **cond)


# schedule_log
def save_schedule_log(o):
    ctx = DBContext()
    ctx.save('cm_schedule_log', o)


def find_schedule_logs(**params):
    sql = ['1=1']
    cond = {}
    ctx = DBContext()
    if 'scheduleid' in params:
        sql.append('and scheduleid = :scheduleid')
        cond['scheduleid'] = params['scheduleid']
    if 'status' in params:
        sql.append('and status = :status')
        cond['status'] = num.safe_int(params['status'])
    return ctx.create_query('cm_schedule_log', ' '.join(sql), **cond)
