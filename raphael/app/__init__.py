# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from flask import Flask
from raphael.utils import setting, logger
from raphael import ArgumentParser


def initialize():
    # parse argument
    ArgumentParser.parse('raphael', 'an OpenLDAP management system', '0.1.0')

    # init setting
    with open(ArgumentParser.args['config']) as _f:
        setting.load(_f)

    # init logger
    logger.initialize()

    # init db
    from raphael.utils.dao import context
    context.DBContext.initialize(context.DBConfig.from_dict(setting.conf.get('dao')))


def create_app():
    initialize()

    app = Flask(__name__)
    flask_config = {
        'SECRET_KEY': setting.conf.get('web').get('cookie_secret'),
        'TEMPLATES_AUTO_RELOAD': True,
    }
    app.config.from_mapping(**flask_config)

    from .modules.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .modules.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from .modules.menu import menu_bp
    app.register_blueprint(menu_bp, url_prefix='/menu')

    from .modules.setting import setting_bp
    app.register_blueprint(setting_bp, url_prefix='/setting')

    from .modules.func import func_bp
    app.register_blueprint(func_bp, url_prefix='/function')

    from .modules.schedule import schedule_bp
    app.register_blueprint(schedule_bp, url_prefix='/schedule')

    from .modules.openldap import openldap_bp
    app.register_blueprint(openldap_bp, url_prefix='/openldap')

    return app
