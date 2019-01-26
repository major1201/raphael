# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import os.path
import sys
from raphael.utils.objects import Singleton
from raphael.utils import setting, logger


class ArgumentParser(Singleton):
    args = None

    @staticmethod
    def parse(project_name, description, version):
        import argparse

        parser = argparse.ArgumentParser(prog=project_name, description=description, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)

        # config file
        etc_config = '/etc/%s/config.yml' % project_name
        default_config = etc_config if os.path.isfile(etc_config) else os.path.join(os.path.dirname(__file__), '..', 'config.yml')
        parser.add_argument('-c', '--config', dest='config', default=default_config, help='specify the config file, default: config.yml')
        ArgumentParser.args = parser.parse_args().__dict__


class Raphael(object):
    def __init__(self, pid_file):
        self.pid_file = pid_file

    def __enter__(self):
        self.prepare_pidfile()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._terminate()

    def _terminate(self):
        self.term_pidfile()

    def terminate(self):
        self._terminate()
        sys.exit()

    def prepare_pidfile(self):
        with open(self.pid_file, 'w') as pid:
            pid.write(str(os.getpid()))

    def term_pidfile(self):
        try:
            os.remove(self.pid_file)
        except:
            pass

    # @staticmethod
    # def prepare_tasks():
    #     from raphael.utils import task
    #     task.load_task_from_database()
    #     task.start()
    #
    # @staticmethod
    # def term_tasks():
    #     from raphael.utils import task
    #     task.shutdown()

    def start_web(self, app=None):
        conf = setting.conf.get('web')
        # signal
        from raphael.utils import system
        system.register_sighandler(self.terminate, 2, 3, 11, 15)

        if app is None:
            from raphael.app import create_app
            app = create_app()
        logger.info('WEB SERVER LISTENING ' + str(conf.get('port')))
        try:
            app.run(
                host=conf.get('listen_addr'),
                port=conf.get('port'),
                debug=conf.get('debug'),
                threaded=conf.get('threaded'),
                use_reloader=False
            )
        except IOError as e:
            import errno
            # skip Interrupted function call in Windows
            if e.errno != errno.EINTR:
                raise
