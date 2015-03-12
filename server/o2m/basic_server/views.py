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

	def get_content(self, markup):
		link = Link.objects.get_query_set()#get_object_or_404(Link, content = self.content_id, friend = 1)

		return json.dumps(link)

	def get(self, request):

		response = HttpResponse()
		print 'Getting usename and password'
		try:
			username = request.GET['username']
			password = request.GET['password']
			print 'Authenticating ' + username
			user = authenticate(username=username, password=password)
			print 'User authenticated as ' + username
			if user is not None:
				if user.is_active:
					login(request, user)
					response = self.get_response(request, user)

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
				response.reason_phrase = 'You are not my friend or that password was wrong'
				response.status_code = 401
		except MultiValueDictKeyError as e:
			response.reason_phrase = 'Give me username and password'
			response.status_code = 401

		if response.status_code != 200: response.content += str(response.status_code) + '  ' + str(response.reason_phrase) 

		return response

def dict_for_node(node):
	result = model_to_dict(node)

	result['friend'] = model_to_dict(Friend.objects.get(pk=result['friend']))
	
	del result['friend']['password']
	del result['parent']

	result['children'] = [dict_for_node(child) for child in node.get_children()]

	return result

def json_for_node(node):
	return json.dumps(dict_for_node(node), indent=4)


class JSONView(AuthenticatedView):
	def get_response(self, request, user):
		response = HttpResponse()
		if self.content_id == 1:
			response.content = json_for_node(Link.objects.filter()[0])
		else:
			response.content = json_for_node(Link.objects.get(content=self.content_id))
		return response

class ContentView(AuthenticatedView):
	def get_response(self, request, user):
		resp = Content.objects.get(pk=self.content_id).get_http_response()
		return resp

def posts(request):
	return JSONView.as_view(content_id = 1)(request)


def content(request, content_id):
	"""Serves content as a file, returning it's guessed Content-Type.
	"""
	return ContentView.as_view(content_id = content_id)(request)

