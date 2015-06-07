
import unittest

import o2m.settings
o2m.settings.DATABASES['default']['NAME'] = 'o2m/db.sqlite3' # Use a local, accessible database

import os, django
os.environ["DJANGO_SETTINGS_MODULE"] = "o2m.settings"
django.setup()

from django.contrib.auth.models import User
from o2m.basic_server.models import NotificationType

from o2m import setup_initial_database
setup_initial_database()


class TestInitialDatabase(unittest.TestCase):
	'''Make sure that the database sent in the distribution contains the correct setup'''

	def test_admin_user(self):
		'''Make sure there is an admin User in the database'''
		self.assertTrue(len(User.objects.filter(username='admin', is_staff=True, is_superuser=True)) > 0)
	
	def test_default_user(self):
		'''Make sure there is a default User in the database'''
		self.assertTrue(len(User.objects.filter(username='user', is_staff=True, is_superuser=True)) > 0)

	def test_notification_types(self):
		'''Make sure there are some notification types in the database'''
		print len(NotificationType.objects.all())
		self.assertTrue(len(NotificationType.objects.all()) == 2)

