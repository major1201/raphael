# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from . import main
from flask import render_template


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error/error.html'), 500
