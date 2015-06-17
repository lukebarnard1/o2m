
import json
from django.http import HttpResponse
from ..models import Friend
from auth import AuthenticatedView
from django.forms.models import model_to_dict

class FriendView(AuthenticatedView):

	friend_id = None

	def must_be_owner(self, request):
		"""You must always be the owner"""
		return True

	def get(self, request):
		response = HttpResponse()

		if self.friend_id == '':
			friends = Friend.objects.exclude(password='NOTFRIENDS')
		else:
			friends = Friend.objects.filter(pk=self.friend_id)

		friend_dicts = []

		for friend in friends:
			friend_dict = model_to_dict(friend)
			friend_dicts.append(friend_dict)

		response.content = json.dumps(friend_dicts)

		return response

	def put(self, request):

		update = json.loads(request.body)

		f = Friend.objects.get(pk=self.friend_id)
		
		for k,v in update.iteritems():
			setattr(f, k, v)
			print '(Server)Updating %s.%s=%s' % (f, k, v)

		f.save()

		return HttpResponse()