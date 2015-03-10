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

class ContentView(View):

	markup = 'html'
	content_id = 1
	id = random.randint(0, 20)
	limit = 3
	password = "pass"

	def get_content(self, markup):
		link = Link.objects.get_query_set()#get_object_or_404(Link, content = self.content_id, friend = 1)

		return json.dumps(link)

	def get(self, request):

		# Authentication required: is this a friend, me or someone else?
		#	- If it is me, html is possible and links are therefore followed.
		#	- If it is not me, only json is possible and links are returned.

		response = HttpResponse()
		print 'Getting...'
		try:
			username = request.GET['username']
			password = request.GET['password']
			print 'Authenticating...'
			user = authenticate(username=username, password=password)
			print 'User...',user
			if user is not None:
				if username != 'Luke Barnard':
					self.markup = 'json'

				if user.is_active:
					login(request, user)
					response.content = self.get_content(self.markup)

					new_password = random_password()

					user.set_password(new_password)
					user.save()

					response['np'] = new_password

					response.reason_phrase = 'Go right ahead and read my posts'
					response.status_code = 200
				else:
					response.reason_phrase = 'You are not my friend anymore'
					response.status_code = 401

			else:
				response.reason_phrase = 'You are not my friend'
				response.status_code = 401
		except MultiValueDictKeyError as e:
			response.reason_phrase = 'Give me username and password ' + str(e)
			response.status_code = 401

		# response.content += str(response.status_code) + '  ' + str(response.reason_phrase) 

		return response

class MainView(TemplateView, ContentView):

	def get_context_data(self, **kwargs):
		self.template_name = 'content.json'

		return {
			'links': Link.objects.all()
		}

class JSONContentView(TemplateView, ContentView):

	template_name = 'content.json'

	def get_context_data(self, **kwargs):
		content = Content.objects.get(pk=self.content_id)
		
		return {
			'content': content.get_html_representation()
		}

def dict_for_node(node):
	result = model_to_dict(node)

	result['friend'] = model_to_dict(Friend.objects.get(pk=result['friend']))
	
	del result['friend']['password']
	del result['parent']

	result['children'] = [dict_for_node(child) for child in node.get_children()]

	return result

def json_for_node(node):
	return json.dumps(dict_for_node(node), indent=4)

def posts(request):
	json = json_for_node(Link.objects.filter()[0])

	return HttpResponse(json)


def content(request, content_id, markup):
	return JSONContentView.as_view(content_id = content_id)(request)

