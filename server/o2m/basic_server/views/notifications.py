import json
from django.http import HttpResponse
from ..models import Friend, Notification, NotificationType
from auth import AuthenticatedView
from django.views.generic import View

class NotificationView(View):
	def must_be_owner(self, request):
		"""In order to view notifications, you must be the owner."""
		return request.method == 'GET'

	def get(self, request):
		"""Respond with all of the notifications on this server"""
		response = HttpResponse()
		notifications = Notification.objects.all()

		notification_dicts = []

		for n in notifications:

			n_dict = {
				'title': n.notification_type.title.format(
					notification=n
				)
			}

			notification_dicts.append(n_dict)

		response.content = json.dumps(notification_dicts)

		return response

	def post(self, request):
		"""Notify the owner of this server of something"""
		response = HttpResponse()
		notification = dict(request.POST)

		notif_keys = notification.keys()

		if not all(n in notif_keys for n in ['obj_id', 'obj_creator', 'notification_type']):
			raise Exception('You must provide obj_id, obj_creator and notification_type')

		notification['notification_type'] = NotificationType.objects.get(name=notification['notification_type'][0])
		try:
			notification['obj_server'] = Friend.objects.get(name=request.GET['username'])
		except Exception as e:
			print 'Not friends. Adding as potential future friend'
			new_friend = Friend.objects.create(name = request.GET['username'], address = request.META['REMOTE_ADDR'], port = 8000, password='NOTFRIENDS')
			new_friend.save()
			notification['obj_server'] = new_friend

		try:
			# notification['obj_creator'] = notification['obj_creator'][0]
			notification['obj_creator'] = Friend.objects.get(name=notification['obj_creator'][0])
		except Exception as e:
			print 'Not friends. Adding notification creator as potential future friend'
			new_friend = Friend.objects.create(name = notification['obj_creator'][0], address = '0.0.0.0', port = 8000, password='NOTFRIENDS')
			new_friend.save()
			notification['obj_creator'] = new_friend

		notification['obj_id'] = notification['obj_id'][0]

		Notification.objects.create(**notification)
		print '(Server)You have a new notification!'
		
		from django.contrib.auth.models import User
		if notification['notification_type'].name == 'Friend request':
			print '\tAnd it\'s a friend request. Checking to see if a request has been sent...'
			new_friend = notification['obj_creator']

			if new_friend.password == 'REQUESTSENT':
				print '\tYes, a request has been sent...'
				new_user = User.objects.create_user(new_friend.name, password=new_friend.password)
				new_user.save()
			else:
				notification['obj_creator'].password = 'REQUESTRECEIVED'
				notification['obj_creator'].save()


		return response