# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from . import schedule_bp
from . import models
from raphael.app import webutils
from flask import request, render_template, g
from raphael.utils import strings, num, task, logger
import json

FUNC_SCHEDULE = ['SYSTEM']


@schedule_bp.route('/')
@webutils.auth(*FUNC_SCHEDULE)
@webutils.menu('scheduler')
def index():
    return render_template('schedule/schedule.html')


@schedule_bp.route('/table', methods=['POST'])
@webutils.auth(*FUNC_SCHEDULE)
@webutils.make_table
def table():
    @webutils.table_batch
    def batch(res):
        for item in res:
            # parse data field
            arr = []
            if item['type'] == 1:  # date
                pass
            elif item['type'] == 2:  # interval
                interval = json.loads(item['data'])
                for field, unit in ('weeks', 'w'), ('days', 'd'), ('hours', 'h'), ('minutes', 'm'), ('seconds', 's'):
                    val = num.safe_int(interval[field])
                    if val:
                        arr.append(str(val) + unit)
                item['data'] = ' '.join(arr)
            elif item['type'] == 3:  # cron
                cron = json.loads(item['data'])
                zero_flag = False
                for field in 'year', 'day_of_week', 'month', 'day', 'hour', 'minute', 'second':
                    if cron[field]:
                        zero_flag = True
                        arr.append(cron[field])
                    else:
                        arr.append('0' if zero_flag else '*')
                item['data'] = ' '.join(reversed(arr))
            # is in current job list
            job = task.get_job(item['id'], models.TASK_DATABASE)
            item['active'] = job is not None
            # add next run
            item['next_run'] = None if job is None else job.next_run_time
        return res

    cond = {}
    if strings.is_not_blank(g.params.get("type", None)):
        cond['type'] = num.safe_int(g.params["type"])
    if strings.is_not_blank(g.params.get("module", None)):
        cond['module'] = g.params["module"]
    if strings.is_not_blank(g.params.get("modulelike", None)):
        cond['modulelike'] = g.params["modulelike"]
    if strings.is_not_blank(g.params.get("sourceid", None)):
        cond['sourceid'] = g.params["sourceid"]
    return models.find_schedules(**cond)


@schedule_bp.route('/save', methods=['POST'])
@webutils.auth(*FUNC_SCHEDULE)
def save():
    schedule_type = num.safe_int(request.form.get('scheduletype'))
    try:
        models.save_schedule_manually({
            'id': request.form.get('oid'),
            'type': schedule_type,
            'data': get_data(schedule_type),
            'starttime': get_time(schedule_type, True),
            'endtime': get_time(schedule_type, False),
            'func': request.form.get('func', None),
            'module': request.form.get('module', None),
            'maxinstance': num.safe_int(request.form.get('maxinstance', 5), 5),
            'enabled': num.safe_int(request.form.get('enabled', None)),
            'args': request.form.get('args', None),
            'sourceid': request.form.get('sourceid', None)
        })
        return 'success'
    except:
        return logger.error_traceback()


def get_data(schedule_type):
    if schedule_type == 1:
        return request.form.get('data_date_utc', '')
    elif schedule_type == 2:
        return strings.to_json({
            'weeks': request.form.get('interval_weeks', None),
            'days': request.form.get('interval_days', None),
            'hours': request.form.get('interval_hours', None),
            'minutes': request.form.get('interval_minutes', None),
            'seconds': request.form.get('interval_seconds', None)
        })
    elif schedule_type == 3:
        return strings.to_json({
            'second': request.form.get('cron_second', None),
            'minute': request.form.get('cron_minute', None),
            'hour': request.form.get('cron_hour', None),
            'day': request.form.get('cron_day', None),
            'month': request.form.get('cron_month', None),
            'day_of_week': request.form.get('cron_day_of_week', None),
            'year': request.form.get('cron_year', None),
        })
    else:
        return None


def get_time(schedule_type, is_start):
    method = 'start' if is_start else 'end'
    if schedule_type == 1:
        return None
    elif schedule_type == 2:
        return strings.strip_to_none(request.form.get('interval_' + method + 'utc', None))
    elif schedule_type == 3:
        return strings.strip_to_none(request.form.get('cron_' + method + 'utc', None))
    else:
        return None


@schedule_bp.route('/get', methods=['POST'])
@webutils.auth(*FUNC_SCHEDULE)
def get():
    schedule = models.get_schedule(request.form.get('id', None))
    return strings.to_json(schedule) if schedule else 'failed'


@schedule_bp.route('/delete', methods=['POST'])
@webutils.auth(*FUNC_SCHEDULE)
def delete():
    models.delete_schedule(request.form.get('id', None))
    return 'success'


@schedule_bp.route('/log/<scheduleid>')
@webutils.auth(*FUNC_SCHEDULE)
@webutils.menu('scheduler')
def log_page(scheduleid):
    return render_template('schedule/schedule_log.html', scheduleid=scheduleid)


@schedule_bp.route('/log/<scheduleid>/table', methods=['POST'])
@webutils.auth(*FUNC_SCHEDULE)
@webutils.make_table
def log_table(scheduleid):
    cond = {'scheduleid': scheduleid}
    status = num.safe_int(g.params.get('status', None))
    if status != 0:
        cond['status'] = status
    return models.find_schedule_logs(**cond)
