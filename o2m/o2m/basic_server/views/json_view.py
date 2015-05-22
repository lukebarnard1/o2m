
import json

from django.http import HttpResponse
from auth import AuthenticatedView

def json_for_node(node):
	if node is None:
		return ''
	else:
		return json.dumps(node.dict_for_node(), indent=4)

class JSONView(AuthenticatedView):

	def get_node_for_json(self):
		return None
	
	def get(self, request):
		response = HttpResponse()
		
		response.content = json_for_node(self.get_node_for_json())
		
		return response