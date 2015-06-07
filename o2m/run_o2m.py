
import socket

#!/usr/bin/env python
import os
import sys

import o2m
from o2m import setup_initial_database
from django.core.management import execute_from_command_line

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "o2m.settings")

	setup_initial_database()

	hostname = socket.gethostname()
	ip = socket.gethostbyname(hostname)
	port = 8000
	new_argv = sys.argv  + ['runserver', '%s:%s' % (ip, port)]
	execute_from_command_line(new_argv)