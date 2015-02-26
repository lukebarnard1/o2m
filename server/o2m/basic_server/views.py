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

def file_path_to_media(file_path):
	return o2m.settings.MEDIA_URL + file_path[len(o2m.settings.O2M_BASE) + 1:]

def read_file(file_path):
	file_path = file_path_to_media(file_path)
	try:
		# print 'o2m.settings.MEDIA_ROOT={0}'.format(o2m.settings.MEDIA_ROOT)
		# print 'o2m.settings.MEDIA_URL={0}'.format(o2m.settings.MEDIA_URL)
		# print 'file_path={0}'.format(file_path)
		# print 'file_path[len(o2m.settings.MEDIA_URL):]={0}'.format(file_path[len(o2m.settings.MEDIA_URL):])
		f = open(os.path.join(o2m.settings.MEDIA_ROOT,file_path[len(o2m.settings.MEDIA_URL):]), 'r')
	except IOError as e:
		return str(e)
	try:
		text = f.read()
		return text
	except IOError as e:
		return 'Failed to read text file at ' + file_path

def file_to_html(file_path):
	file_type = file_path[file_path.rindex('.') + 1:].lower()

	if file_type in ['txt', 'html']:
		text = read_file(file_path)

		if file_type == 'txt':
			return '<p>{0}</p>'.format(escape(text))
		elif file_type == 'html':
			return text

	elif file_type == 'png' or file_type == 'jpg':
		return '<img src="{0}" width="200" alt="{0}">'.format(file_path)

	return 'Unknown file type'


class ContentView(View):

	markup = 'html'
	content_id = 1
	id = random.randint(0, 20)
	limit = 3
	password = "pass"

	# def traverse_posts(self, link = 1, limit = 10):
	# 	"""Starting from a particular link, traverse link edges, which
	# 	are pairs of links until either there are no more child nodes
	# 	to traverse or the recursion depth limit is met. Returns a
	# 	dictionary containing links and content in the tree of links.
	# 	Some content will not have any children. Others won't have a
	# 	children list at all - these are links to friend's content.
	# 	"""
	# 	django_link = Link.objects.get(pk = link)
	# 	django_content = django_link.get_content()

	# 	if django_content:
	# 		content = model_to_dict(django_content)

	# 		content['creation_time'] = content['creation_time'].__str__()
	# 		content['children'] = []
	# 		content['file_path'] = file_path_to_media(content['file_path'])
	# 		if limit > 1:

	# 			link_edges = LinkEdge.objects.filter(a = link)
				
	# 			if len(link_edges) > 0:
	# 				for edge in link_edges:
	# 					child = self.traverse_posts(child, limit - 1)
	# 					content['children'].append(child)
	# 		return content
	# 	else:
	# 		link = model_to_dict(django_link)
	# 		link['friend'] = model_to_dict(django_link.friend)
	# 		return link

	def get_content(self):
		print self.__str__() + ".get_content()"
		link = get_object_or_404(Link, content = self.content_id, friend = 1)
		# content = self.traverse_posts(link.id)
		return self.render(self.markup, link)

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
					response.content = self.get_content()

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
			response.reason_phrase = 'Give me username and password',e
			response.status_code = 401

		return response

	def render(self, markup, content):
		if markup == 'html':
			return self.render_html(content)
		elif markup == 'json':
			return self.render_json(content)
		else:
			raise Exception('Format not supported')

	def render_json(self, content):
		return json.dumps(content)

	def content_from_friend(self, link):
		friend = link.friend
		html = ''
		print 'Trying to get content from {0} with password {1} and ip {2}'.format(friend.name, friend.password, friend.address)

		source_address = '/content/{0}.json'.format(link.content)
		con = httplib.HTTPConnection(friend.address, friend.port)
		try:
			con.request('GET', source_address + '?' + urllib.urlencode({'username':'Luke Barnard', 'password': friend.password}))
			resp = con.getresponse()

			#Retrieve new password for request next time
			new_password = resp.getheader('np')

			if new_password is not None:
				print 'New password for {0} is {1}'.format(friend.name, new_password)

				friend.password = new_password
				friend.save()

			js = resp.read()
			try:
				loaded_content = json.loads(js)

				class TempLink():
					def __init__(self, loaded_content):
						self.loaded_content = loaded_content

					def get_content(self):
						return self.loaded_content

				populated_link = TempLink(loaded_content)

				html += '<li class="media"><h4>Linked from {1}:</h4></li>{0}'.format(self.render_html(populated_link), friend.name)
			except Exception as e:

				html += 'Failed to get JSON: '+ str(resp.status) + ' - ' + str(resp.reason) + ' ' + str(e) + '<br>'
				if resp.status == 500: html += 'Response text: ' + js
		finally:
			con.close()
		return html

	def render_html(self, link):
		html = '<li class="content media"><div class="media-left">'+'</div><div class="media-body">' 
		content = link.get_content()
		if content:
			# Not a link
			html += file_to_html(content.file_path)

			html += '<ul class="children media-list">'
			
			for child in link.children.iterator():
				print child
				html += self.render_html(child)
			html += '</ul>'
		else:
			html += '<ul class="link media-list">'
			# It is a link
			print self.limit
			if self.limit > 0:
				self.limit -= 1

				html += self.content_from_friend(link)
			else:
				# Print the link for following
				href = 'http://{0}:{1}/content/{2}'.format(content['friend']['address'], str(content['friend']['port']), str(content['content']))

				html += '<a href="' + href + '">Link to ' + content['friend']['name'] + '/' + str(content['content']) + '</a>'
			html += '</ul>'

		html += '</div></li>'
		return html

class MainView(TemplateView, ContentView):

	def get_context_data(self, **kwargs):

		if self.markup == 'html':
			self.template_name = 'content.html'
		elif self.markup == 'json':
			self.template_name = 'content.json'

		return {
			'content': self.get_content()
		}

def posts(request, markup):
	if markup:
		return MainView.as_view(markup = markup, content_id = 1)(request)
	else:
		return MainView.as_view(content_id = 1)(request)


def content(request, content_id, markup):
	if markup is not None:
		return ContentView.as_view(markup = markup, content_id = content_id)(request)
	else:
		return ContentView.as_view(content_id = content_id)(request)

