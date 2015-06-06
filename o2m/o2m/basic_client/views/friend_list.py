
from django.views.generic import TemplateView
from auth import AuthenticatedView
from o2m.basic_server.models import Friend

class FriendListView(AuthenticatedView, TemplateView):
	template_name = "friends.html"

	def get_context_data(self, **kwargs):
		me = Friend.objects.get(name=self.username)

		source_address = '/friend/'

		response_headers = None

		try:
			response_headers, content = get_from_friend(source_address, me, me)
		except Exception as e:
			print "Loading notifications data from {0} failed: {1}".format(me.name, e)

		if response_headers is not None:
			if response_headers['status'] == '200':
				friends = json.loads(content)

				return {'friends' : friends,
						'me' : model_to_dict(me)}

def friends(request):
	return FriendListView.as_view()(request)