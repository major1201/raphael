# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from flask import Blueprint

func_bp = Blueprint('func', __name__)

from . import views
