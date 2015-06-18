#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os.path import abspath, dirname
import sys

# Add the parent directory of 'manage.py' to the python path, so manage.py can
# be run from any directory.  From http://www.djangosnippets.org/snippets/281/
sys.path.insert(0, dirname(dirname(abspath(__file__))))

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baobab.settings')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
