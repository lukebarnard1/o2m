
def setup_initial_database():
	from django.core.management import execute_from_command_line

	execute_from_command_line(['manage.py','makemigrations'])
	execute_from_command_line(['manage.py','migrate'])

	from django.contrib.auth.models import User
	print 'Printing users:'
	users = User.objects.all()
	print users

	if len(users) == 0:
		print 'Adding initial users: user and admin, both with password \'password\''
		user = User.objects.create_user(o2m.settings.DEFAULT_USERNAME, password='password')
		admin = User.objects.create_user('admin', password='password')
		user.is_superuser = True
		user.is_staff = True
		admin.is_superuser = True
		admin.is_staff = True
		user.save()
		admin.save()
		print 'Printing users after additional users were added:'
		users = User.objects.all()
		print users

	from o2m.basic_server.models import Friend

	print 'Printing friends:'
	friends = Friend.objects.all()
	print friends

	if len(friends) == 0:
		print 'Adding initial friend:'
		Friend.objects.create(name=o2m.settings.DEFAULT_USERNAME, password='password', address='127.0.0.1', port='8000').save()
		print 'Printing friends after initial friend was added:'
		friends = Friend.objects.all()
		print friends