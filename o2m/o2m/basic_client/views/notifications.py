from auth import AuthenticatedView
from django.views.generic import TemplateView
from o2m.basic_server.models import Friend
from o2m.basic_client.views import get_from_friend
import json

class NotificationView(AuthenticatedView, TemplateView):
	template_name = "notifications.html"

	def get_context_data(self, **kwargs):
		me = Friend.objects.get(name=self.username)
		print "(Client)Me:",me

		source_address = '/notifications/'

		response_headers = None

		try:
			response_headers, content = get_from_friend(source_address, me, me)
		except Exception as e:
			print "Loading notifications data from {0} failed: {1}".format(me.name, e)

		if response_headers is not None:
			if response_headers['status'] == '200':
				notifications = json.loads(content)

				return {'notifications' : notifications,
						'me' : model_to_dict(me)}

def notifications(request):
	return NotificationView.as_view()(request)