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

		if self.markup == 'html':
			self.template_name = 'content.html'
		elif self.markup == 'json':
			self.template_name = 'content.json'

		return {
			'links': Link.objects.all()
		}

class JSONView(TemplateView, ContentView):

	template_name = 'content.json'

	def get_context_data(self, **kwargs):
		# raw_input('JSONView.get_context_data')

		return {
			'links': Link.objects.all()
		}

def posts(request, markup):
	if markup:
		return MainView.as_view(markup = markup, content_id = 1)(request)
	else:
		return MainView.as_view(content_id = 1)(request)


def content(request, content_id, markup):
	return JSONView.as_view(content_id = content_id)(request)

