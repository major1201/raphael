# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function
import yaml
from raphael.utils import num

conf = None


def load(stream):
    global conf
    conf = yaml.load(stream)


def get(name, dv=None):
    from raphael.app.modules.setting.models import CmSettingCache
    obj = CmSettingCache.get(name)
    if obj:
        return obj['value']
    return dv


def get_int(name, dv=0):
    return num.safe_int(get(name), dv)


def get_bool(name, dv=False):
    true = ['true', 'yes', '1']
    false = ['false', 'no', '0']
    real_val = get(name)
    if real_val is None:
        return dv
    if str.lower(real_val) in true:
        return True
    elif str.lower(real_val) in false:
        return False
    return dv
