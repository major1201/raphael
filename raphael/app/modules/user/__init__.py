# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from flask import Blueprint

user_bp = Blueprint('user', __name__)

from . import views
