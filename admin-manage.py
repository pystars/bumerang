#!/usr/bin/env python
import os, sys

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bumerang.settings')
    os.environ.setdefault('DJANGO_CONFIGURATION', 'AdminSettings')

    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)
