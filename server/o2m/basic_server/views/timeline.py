
import json

from django.http import HttpResponse
from auth import AuthenticatedView
from ..models import Link

class TimelineView(AuthenticatedView):
	def get(self, request):
		print '(Server)Getting timeline'
		response = HttpResponse()
		
		timeline = Link.objects.filter(parent = None).order_by('-creation_time')
		
		timeline_dicts = []

		for post in timeline:
			timeline_dicts.append(post.dict_for_node())
			
		response.content = json.dumps(timeline_dicts)

		return response