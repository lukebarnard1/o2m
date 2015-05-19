
from ..models import Friend

def dict_for_node(node):
	result = model_to_dict(node)
	result['creation_time'] = node.creation_time.__str__()

	result['friend'] = model_to_dict(Friend.objects.get(pk=result['friend']))
	
	del result['friend']['password']
	del result['parent']

	result['children'] = [dict_for_node(child) for child in node.get_children().order_by('-creation_time')]

	return result

def notify(me, notification_type, creator, obj, receiver):
	notification = {
		'notification_type': notification_type, 
		'obj_id': obj.id,
		'obj_creator': creator.name,
	}

	response = receiver.send_notification(me, notification)
	print response.reason

from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.utils.html import escape
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import authenticate, login

from auth import AuthenticatedView
from notifications import NotificationView
from json_view import JSONView
from timeline import TimelineView
from links import LinkView
from content import ContentView

import traceback

def posts(request):
	try:
		return LinkView.as_view(content_id = 1)(request)
	except Exception as e:
		traceback.print_exc()

def link(request, content_id):
	try:
		return LinkView.as_view(content_id = content_id)(request)
	except Exception as e:
		traceback.print_exc()

def content(request, content_id):
	"""Serves content as a file, returning it's guessed Content-Type.
	"""
	try:
		return ContentView.as_view(content_id = content_id)(request)
	except Exception as e:
		traceback.print_exc()

def timeline(request):
	try:
		return TimelineView.as_view()(request)
	except Exception as e:
		traceback.print_exc()

def notifications(request):
	try:
		return NotificationView.as_view()(request)
	except Exception as e:
		traceback.print_exc()


