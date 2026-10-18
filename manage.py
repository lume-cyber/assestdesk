#!/usr/bin/env python
import os, sys
from config.hosting import load_hosting_environment
load_hosting_environment()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from django.core.management import execute_from_command_line
execute_from_command_line(sys.argv)
