# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler import events

_scheduler = BackgroundScheduler()


def start():
    _scheduler.start()
    # add listener
    _scheduler.add_listener(task_execution_listener, events.EVENT_JOB_EXECUTED | events.EVENT_JOB_ERROR | events.EVENT_JOB_MISSED | events.EVENT_JOB_MAX_INSTANCES)


def shutdown(wait=True):
    try:
        _scheduler.shutdown(wait)
    except:
        pass


def task_execution_listener(e):
    from apscheduler.events import JobExecutionEvent
    from raphael.app.modules.schedule import models as schedule
    from raphael.utils.dao.context import DBContext

    assert isinstance(e, JobExecutionEvent)
    # add to task schedule history database
    if e.jobstore == schedule.TASK_DATABASE:
        status_dict = {events.EVENT_JOB_EXECUTED: 1, events.EVENT_JOB_ERROR: 2, events.EVENT_JOB_MISSED: 3, events.EVENT_JOB_MAX_INSTANCES: 4}
        _schedule = schedule.get_schedule(e.job_id)
        if _schedule is not None:
            with DBContext():
                if _schedule.get('type') == 1:
                    _schedule['enabled'] = 0
                    schedule.save_schedule(_schedule)
                schedule_log = {
                    'scheduleid': e.job_id,
                    'executiontime': e.scheduled_run_time,
                    'retval': None if e.retval is None else str(e.retval),
                    'status': status_dict[e.code],
                    'exception': str(e.exception)
                }
                schedule.save_schedule_log(schedule_log)


def add_cron_job(func, job_id=None, job_store='default', args=None, kwargs=None, max_instances=5, year=None, month=None, day=None, week=None,
                 day_of_week=None, hour=None, minute=None, second=None, start_date=None, end_date=None, timezone=None):
    trigger = CronTrigger(year, month, day, week, day_of_week, hour, minute, second, start_date, end_date, timezone)
    _scheduler.add_job(func, id=job_id, jobstore=job_store, args=args, kwargs=kwargs, max_instances=max_instances, trigger=trigger, replace_existing=True)


def add_date_job(func, job_id=None, job_store='default', args=None, kwargs=None, max_instances=5, run_date=None, timezone=None):
    trigger = DateTrigger(run_date, timezone)
    _scheduler.add_job(func, id=job_id, jobstore=job_store, args=args, kwargs=kwargs, max_instances=max_instances, trigger=trigger, replace_existing=True)


def add_interval_job(func, job_id=None, job_store='default', args=None, kwargs=None, max_instances=5,
                     weeks=0, days=0, hours=0, minutes=0, seconds=0, start_date=None, end_date=None, timezone=None):
    trigger = IntervalTrigger(weeks, days, hours, minutes, seconds, start_date, end_date, timezone)
    _scheduler.add_job(func, id=job_id, jobstore=job_store, args=args, kwargs=kwargs, max_instances=max_instances, trigger=trigger, replace_existing=True)


def get_job(job_id, job_store=None):
    return _scheduler.get_job(job_id, jobstore=job_store)


def list_jobs(job_store=None):
    return _scheduler.get_jobs(job_store)


def remove_job(job_id, job_store=None):
    _scheduler.remove_job(job_id, jobstore=job_store)


def remove_all_jobs(job_store=None):
    _scheduler.remove_all_jobs(job_store)


def load_task_from_database():
    from raphael.utils import logger
    from raphael.app.modules.schedule import models as schedule

    # add new jobstore
    try:
        _scheduler.remove_jobstore(schedule.TASK_DATABASE)
    except:
        pass
    _scheduler.add_jobstore(MemoryJobStore(), schedule.TASK_DATABASE)
    # clear the jobstore
    remove_all_jobs(schedule.TASK_DATABASE)
    # add add tasks
    schedule_list = schedule.find_schedules(enabled=1).fetch()
    for item in schedule_list:
        try:
            schedule.save_task_schedule(item)
        except:
            logger.error_traceback()
