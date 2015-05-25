
import json
from django.http import HttpResponse
from django.forms.models import model_to_dict
from ..models import Content
from auth import AuthenticatedView

class ContentListView(AuthenticatedView):

	def must_be_owner(self, request):
		"""You must always be the owner"""
		return True

	def get(self, request):

		content_list = Content.objects.all()

		dict_list = [model_to_dict(c) for c in content_list]

		json_list = json.dumps(dict_list)

		return HttpResponse(json_list)