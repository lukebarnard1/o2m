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

from basic_server.models import Link, Content, Friend, Notification, NotificationType

import o2m
import os
import json
import httplib
import urllib
import random
import string

def random_password():
	return "".join([random.choice(string.ascii_letters + string.digits + ".-") for i in xrange(32)])

class AuthenticatedView(View):

	content_id = 1
	limit = 3

	def must_be_owner(self, request):
		"""True if the username and password should be the owner
		of the server.
		"""
		return False

	def dispatch(self, request, *args, **kwargs):
		response = HttpResponse()

		try:
			username = request.GET['username']
			password = request.GET['password']

		except MultiValueDictKeyError as e:
			response.reason_phrase = 'Give me username and password'
			response.status_code = 401
			return response

		print '(Server)Authenticating ' + username
		user = authenticate(username=username, password=password)
		if user is not None:
			print '(Server)User authenticated as ' + username
			if user.is_active:
				print '(Server)Logging in...'
				login(request, user)

				if not self.must_be_owner(request) or username == o2m.settings.ME:
					print '(Server)Dispatching...'
					response = super(AuthenticatedView, self).dispatch(request, *args, **kwargs)

					new_password = random_password()

					user.set_password(new_password)
					user.save()

					response['np'] = new_password
				else:
					response.reason_phrase = 'Only the owner can do that'
					response.status_code = 401
			else:
				response.reason_phrase = 'You are not my friend anymore'
				response.status_code = 401

		else:
			response.reason_phrase = 'You are not my friend or that password was wrong'
			response.status_code = 401
		
		# Display simple content to display error for slightly easier debug
		if response.status_code != 200: response.content += str(response.status_code) + '  ' + str(response.reason_phrase) 

		return response

def dict_for_node(node):
	result = model_to_dict(node)
	result['creation_time'] = node.creation_time.__str__()

	result['friend'] = model_to_dict(Friend.objects.get(pk=result['friend']))
	
	del result['friend']['password']
	del result['parent']

	result['children'] = [dict_for_node(child) for child in node.get_children().order_by('-creation_time')]

	return result

def json_for_node(node):
	if node is None:
		return ''
	else:
		return json.dumps(dict_for_node(node), indent=4)


class JSONView(AuthenticatedView):

	def get_node_for_json(self):
		return None
	
	def get(self, request):
		response = HttpResponse()
		
		response.content = json_for_node(self.get_node_for_json())
		
		return response

class TimelineView(AuthenticatedView):
	def get(self, request):
		print '(Server)Getting timeline'
		response = HttpResponse()
		
		timeline = Link.objects.filter(parent = None).order_by('-creation_time')
		
		timeline_dicts = []

		for post in timeline:
			timeline_dicts.append(dict_for_node(post))
			
		response.content = json.dumps(timeline_dicts)
		print response.content
		
		return response

def notify(me, notification_type, obj, receiver):
	notification = {
		'notification_type': notification_type, 
		'objid': obj.id
	}

	receiver.send_notification(me, notification)

class LinkView(JSONView):

	content_id = 1

	def must_be_owner(self, request):
		"""You must be owner to add a child link to the link
		that refers to content 1. Deletion authentication is
		handled in the delete method."""
		return request.method == 'POST' and self.content_id == 1

	def get_node_for_json(self):
		if self.content_id == 1:
			try:
				return Link.objects.filter()[0]
			except IndexError as e:
				return None
		else:
			return Link.objects.get(content=self.content_id)

	def notify_content_owners(self, me, node, friend_posting):
		"""Notify the owner of a node that someone has added
		content as a descendant of it."""

		notify(me, 'content_add', friend_posting, node.friend)

		if node.parent:
			self.notify_content_owners(me, node.parent, friend_posting)

	def post(self, request):
		"""Add a post based on the request.

		POST variables must include 'content_id' to assign the 
		ID of the related content, which may not be on the 
		same machine as the link.

		This method currently assumes that the content will be
		there."""
		potential_parents = Link.objects.filter(content = self.content_id)

		print '(Server)Adding link to first of ',potential_parents

		if len(potential_parents):
			parent = potential_parents[0]
		else:
			parent = None

		friend = Friend.objects.get(name = request.user.username)
		try:
			content = request.POST['content_id']

		except MultiValueDictKeyError as e:
			r = HttpResponse()
			r.status = 501
			r.reason = 'No content id specified'
			return r

		link = Link.objects.create(friend = friend, content = content)
		link.parent = parent
		link.save()

		me = Friend.objects.get(name=o2m.settings.ME)

		if parent:
			self.notify_content_owners(me, parent, friend)

		return HttpResponse('Link added')

	def delete(self, request):
		"""Delete a link from the tree and any links below it.

		This does not affect content."""

		link = Link.objects.get(content = self.content_id)

		friend = Friend.objects.get(name = request.user.username)
		
		if link.friend.id == friend.id:
			link.delete()
			return HttpResponse('Link deleted')
		else:
			r = HttpResponse()
			r.status = 403
			r.reason = 'You can only delete links that you created'
			return r

class ContentView(AuthenticatedView):

	def must_be_owner(self, request):
		"""You must always be the owner to add or delete content"""
		return request.method in ('POST', 'DELETE')

	def get(self, request):
		try:
			resp = Content.objects.get(pk=self.content_id).get_http_response()
		except Exception as e:
			print "(Server){0}".format(e)
			resp = HttpResponse('Could not find that content')
			resp.reason_phrase = 'Could not find that content'
			resp.status_code = 404
		return resp

	def post(self, request):
		content_text = request.POST['content_text']
		content_id = self.content_id
		content_file_name = o2m.settings.O2M_BASE + '/' + content_id + '.html'

		print '(Server)Using content_id {0} for content filename (but not for the actual id yet)'.format(content_id)

		try:
			f = open(content_file_name, 'w')
			f.write(content_text)
		except Exception as e:
			print "(Server){0}".format(e)
		finally:
			f.close()

		content = Content.objects.create(file_path = content_file_name)
		content.save()

		return HttpResponse(json.dumps({'content_id' : content.pk}))

	def delete(self, request):
		try:
			content = Content.objects.get(pk = self.content_id)
			content.delete()

			return HttpResponse('Content deleted')
		except Exception as e:
			print "(Server){0}".format(e)
			resp = HttpResponse('Could not delete that content')
			resp.reason_phrase = 'Could not delete that content'
			resp.status_code = 404
			return resp

class NotificationView(AuthenticatedView):
	def must_be_owner(self, request):
		"""In order to view notifications, you must be the owner."""
		return request.method == 'GET'

	def get(self, request):
		response = HttpResponse()
		notifications = Notification.objects.all()

		notification_dicts = []

		for n in notifications:
			import models
			ObjectModel = getattr(models, n.notification_type.objtype)

			n.object = ObjectModel.objects.get(pk=n.objid)

			n_dict = {
				'title': n.notification_type.title.format(
					notification=n
				)
			}

			notification_dicts.append(n_dict)

		response.content = json.dumps(notification_dicts)

		return response

	def post(self, request):
		response = HttpResponse()
		notification = dict(request.POST)

		notif_keys = notification.keys()

		if notif_keys == ['objid', 'notification_type']:
			raise Exception('You must provide objid and notification_type')

		notification['friend'] = Friend.objects.get(name=request.user.username)
		notification['objid'] = notification['objid'][0]
		notification['notification_type'] = NotificationType.objects.get(name=notification['notification_type'][0])

		Notification.objects.create(**notification)

		return response

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
	try:
		return NotificationView.as_view()(request)
	except Exception as e:
		import traceback
		traceback.print_exc()


