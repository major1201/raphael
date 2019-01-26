# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from flask import Blueprint

setting_bp = Blueprint('setting', __name__)

from . import views
