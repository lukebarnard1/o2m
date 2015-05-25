
import json
from django.http import HttpResponse
from ..models import Friend
from auth import AuthenticatedView

class FriendView(AuthenticatedView):

	friend_id = None

	def must_be_owner(self, request):
		"""You must always be the owner"""
		return True

	def put(self, request):

		update = json.loads(request.body)

		f = Friend.objects.get(pk=self.friend_id)
		
		for k,v in update.iteritems():
			setattr(f, k, v)
			print '(Server)Updating %s.%s=%s' % (f, k, v)

		f.save()

		return HttpResponse()