# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import os
import raphael.app
from raphael import Raphael
from raphael.utils import setting

app = raphael.app.create_app()


if __name__ == '__main__':
    pid_file = os.path.join(os.path.dirname(__file__), setting.conf.get('system').get('project_name') + '.pid')
    with Raphael(pid_file) as raphael:
        # raphael.prepare_tasks()
        raphael.start_web(app)
