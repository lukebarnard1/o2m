import json
from django.http import HttpResponse
from ..models import Friend, Notification, NotificationType
from auth import AuthenticatedView

class NotificationView(AuthenticatedView):
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
		notification['obj_server'] = Friend.objects.get(name=request.user.username)
		try:
			notification['obj_creator'] = Friend.objects.get(name=notification['obj_creator'][0])
		except Exception as e:
			response = HttpResponse('Cannot notify - not friends')
			response.reason_phrase = 'Cannot notify - not friends (%s)' % e
			response.status_code = 401
			return response
		notification['obj_id'] = notification['obj_id'][0]

		Notification.objects.create(**notification)

		return response