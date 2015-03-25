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

from basic_server.models import Link, Content, Friend

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

	def must_be_owner(self):
		"""True if the username and password should be the owner
		of the server.
		"""
		return False

	def get_authenticated_response(self, request, username, password):
		response = HttpResponse()
		print '(Server)Authenticating ' + username
		user = authenticate(username=username, password=password)
		if user is not None:
			print '(Server)User authenticated as ' + username
			if user.is_active:
				login(request, user)

				if not self.must_be_owner() or username == o2m.settings.ME:
					response = self.get_response(request, user)

					new_password = random_password()

					user.set_password(new_password)
					user.save()

					response['np'] = new_password

					response.reason_phrase = 'Go right ahead and read my posts'
					response.status_code = 200
				else:
					response.reason_phrase = 'Only the owner can do that'
					response.status_code = 401
			else:
				response.reason_phrase = 'You are not my friend anymore'
				response.status_code = 401

		else:
			response.reason_phrase = 'You are not my friend or that password was wrong'
			response.status_code = 401
		return response

	def post(self, request): 
		response = HttpResponse()
		print '(Server)Getting username and password'
		print request.GET
		try:
			username = request.GET['username']
			password = request.GET['password']
			
			response = self.get_authenticated_response(request, username, password)

		except MultiValueDictKeyError as e:
			response.reason_phrase = 'Give me username and password'
			response.status_code = 401

		if response.status_code != 200: response.content += str(response.status_code) + '  ' + str(response.reason_phrase) 

		print "(Server)Returning: {0} because {1}".format(response.status_code, response.reason_phrase)

		return response


	def get(self, request):
		response = HttpResponse()
		print '(Server)Getting username and password'
		try:
			username = request.GET['username']
			password = request.GET['password']
			
			response = self.get_authenticated_response(request, username, password)

		except MultiValueDictKeyError as e:
			response.reason_phrase = 'Give me username and password'
			response.status_code = 401

		if response.status_code != 200: response.content += str(response.status_code) + '  ' + str(response.reason_phrase) 

		print "(Server)Returning: {0} because {1}".format(response.status_code, response.reason_phrase)

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
	return json.dumps(dict_for_node(node), indent=4)


class JSONView(AuthenticatedView):

	def get_node_for_json(self):
		return Link.objects.filter()[0]
	
	def get_response(self, request, user):
		response = HttpResponse()
		
		response.content = json_for_node(self.get_node_for_json())
		
		return response

class PostsView(JSONView):
	def get_node_for_json(self):
		if self.content_id == 1:
			return Link.objects.filter()[0]
		else:
			return Link.objects.get(content=self.content_id)

class ContentView(AuthenticatedView):
	def get_response(self, request, user):
		resp = Content.objects.get(pk=self.content_id).get_http_response()
		return resp

class TimelineView(JSONView):
	def get_response(self, request, user):
		response = HttpResponse()
		
		timeline = Link.objects.filter(parent = None).order_by('-creation_time')
		
		timeline_dicts = []

		for post in timeline:
			timeline_dicts.append(dict_for_node(post))
			
		response.content = json.dumps(timeline_dicts)
		
		return response

class AddLink(AuthenticatedView):

	parent_content_id = 1

	def must_be_owner(self):
		"""You must be ownser to add a child link to the link
		that refers to content 1."""
		return self.parent_content_id == 1

	def get_response(self, request, user):
		"""Add a post based on the request.

		POST variables must include 'content_id' to assign the 
		ID of the related content, which may not be on the 
		same machine as the link.

		This method currently assumes that the content will be
		there."""
		potential_parents = Link.objects.filter(content = self.parent_content_id)
		print '(Server)Adding link to first of ',potential_parents
		if len(potential_parents):
			parent = potential_parents[0]
		else:
			parent = None

		friend = Friend.objects.get(name = user.username)
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

		# try:
		# 	Link.objects.insert_node(parent, link, save=True)
		# except Exception as e:
		# 	print e

		return HttpResponse('Link added')

class AddContent(AuthenticatedView):

	def must_be_owner(self):
		"""You must always be the owner to add content"""
		return True

	def get_response(self, request, user):
		""""""

		content_text = request.POST['content_text']
		content_id = self.content_id
		content_file_name = o2m.settings.O2M_BASE + '/' + content_id + '.html'

		print '(Server)Using content_id {0} for content filename (but not for the actual id yet)'.format(content_id)

		try:
			f = open(content_file_name, 'w')
			f.write(content_text)
		finally:
			f.close()

		content = Content.objects.create(file_path = content_file_name)
		content.save()

		return HttpResponse(json.dumps({'content_id' : content.pk}))

def posts(request):
	if request.method == 'GET':
		return PostsView.as_view(content_id = 1)(request)
	elif request.method == 'POST':
		return AddLink.as_view(parent_content_id = 1)(request)

def add_link(request, content_id):
	return AddLink.as_view(parent_content_id = content_id)(request)

def content(request, content_id):
	"""Serves content as a file, returning it's guessed Content-Type.
	"""
	if request.method == 'GET':
		return ContentView.as_view(content_id = content_id)(request)
	elif request.method == 'POST':
		return AddContent.as_view(content_id = content_id)(request)

def timeline(request):
	return TimelineView.as_view()(request)


