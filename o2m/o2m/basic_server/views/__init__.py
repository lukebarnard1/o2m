import traceback

from ..models import Friend

from auth import AuthenticatedView
from notifications import NotificationView
from json_view import JSONView
from timeline import TimelineView
from links import LinkView
from content import ContentView

from django.forms.models import model_to_dict

def posts(request):
	return LinkView.as_view(content_id = 1)(request)
	
def link(request, content_id):
	return LinkView.as_view(content_id = content_id)(request)
	
def content(request, content_id):
	"""Serves content as a file, returning it's guessed Content-Type.
	"""
	return ContentView.as_view(content_id = content_id)(request)
	
def timeline(request):
	return TimelineView.as_view()(request)
	
def notifications(request):
	return NotificationView.as_view()(request)
	

