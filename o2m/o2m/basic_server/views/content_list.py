
import json
from django.http import HttpResponse
from django.forms.models import model_to_dict
from ..models import Content
from auth import AuthenticatedView

class ContentListView(AuthenticatedView):

	mime_type = None

	def must_be_owner(self, request):
		"""You must always be the owner"""
		return True

	def get(self, request):

		content_list = Content.objects.all()
		
		if self.mime_type == None:
			dict_list = [model_to_dict(c) for c in content_list]
		else:
			dict_list = [model_to_dict(c) for c in content_list if c.get_mime_type()==self.mime_type]
			print c.get_mime_type()

		json_list = json.dumps(dict_list)

		return HttpResponse(json_list)