

import httplib, urllib
import json
import dateutil.parser

from django import forms
from django.http import HttpResponse
from django.views.generic import TemplateView
from basic_server.models import Link, Content, Friend
from django.forms.models import model_to_dict
from django.shortcuts import redirect
import o2m, o2m.settings
import random
import string

def random_content_name():
	return "".join([random.choice(string.ascii_letters + string.digits + "-") for i in xrange(32)])

def get_authenticated_link(source_address, me, friend):
	return source_address + '?' + urllib.urlencode({'username':me.name, 'password': friend.password})

def get_from_friend(source_address, friend , me, method = 'GET', variables = {}):
	print "(Client)Logging into {0} as {1} to do {2} with {3} with URI {4} ".format(friend, me, method, variables, source_address)
	try:
		con = httplib.HTTPConnection(friend.address, friend.port)
		con.request(method, get_authenticated_link(source_address, me, friend), urllib.urlencode(variables) ,{"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"})
		resp = con.getresponse()

		#Retrieve new password for request next time
		new_password = resp.getheader('np')

		if new_password is not None:
			friend.password = new_password
			friend.save()
		print "(Client)Getting {0} has given the new password {1} to access {2}".format(source_address, friend.password, friend.name)
	finally:
		con.close()
	return resp

def link_to_html(link, friend, me):
	content_link = '/content/{0}'.format(link['content']) 
	
	resp = get_from_friend(content_link, friend, me)

	content_type = resp.getheader('Content-Type')
	if content_type == 'text/html':
		return resp.read()
	elif content_type.startswith('image'):
		"""
		TODO: Fix with caching the image


		"""
		# This should not be used because the new password gets given to the browser, which does nothing with it!
		# html += '<img src="{0}" width="100">'.format(get_authenticated_link(content_link, me, friend))
		return '<img src="{0}" width="100">'.format('https://www.google.ch/images/srpr/logo11w.png')

class TimelineView(TemplateView):
	template_name = "timeline.html"

	#Whether the posts are mine or my friends as well
	just_me = False

	class CommentForm(forms.Form):
	    content_text = forms.CharField(label='Comment', max_length=128)
	
	class PostForm(forms.Form):
	    content_text = forms.CharField(label='Post')

	def get_context_data(self, **kwargs):

		me = Friend.objects.get(name=o2m.settings.ME)
		print "(Client)Me:",me

		source_address = '/timeline'

		if self.just_me:
			friends = [Friend.objects.filter()[0]]
		else:
			friends = Friend.objects.filter()

		timeline = []

		def assign_links_address(links):
			for link in links:
				link['address'] = friend.address
				link['port'] = friend.port
				if len(link['children']):
					assign_links_address(link['children'])
			return links

		for friend in friends:
			resp = None
			try:
				resp = get_from_friend(source_address, friend, me)
			except Exception as e:
				print "Loading timeline data from {0} failed: {1}".format(friend.name, e)

			if resp is not None :
				print "(Client)Got {0} '{1}' whilst accessing {2}".format(resp.status, resp.reason, friend.name)
				if resp.status == 200: 
					content = resp.read()
					links_from_friend = json.loads(content)

					links_from_friend = assign_links_address(links_from_friend)

					timeline.extend(links_from_friend)

		def newest_first(a, b):
			t1 = dateutil.parser.parse(a['creation_time'])
			t2 = dateutil.parser.parse(b['creation_time'])
			return int((t2 - t1).total_seconds())

		timeline = sorted(timeline, cmp = newest_first)

		def recurse(lst, func, children_key = 'children'):
			for item in lst:
				item = func(item)
				children = item[children_key]
				if len(children):
					recurse(children, func)

		def parse_time(link):
			link['creation_time'] = dateutil.parser.parse(link['creation_time'])
			return link

		recurse(timeline, parse_time)

		def get_children_indented(children, level = 0):
			flat_children = []

			for link in children:
				link['level'] = range(level + 1)
				flat_children.append(link)
				if len(link['children']):
					flat_children.extend(get_children_indented(link['children'], level = level + 1))

			return flat_children

		links = get_children_indented(timeline)

		for link in links:
			friend = Friend.objects.get(address = link['friend']['address'], port = link['friend']['port'])
			try:
				link['html'] = link_to_html(link, friend, me)
			except:
				link['html'] = None

		links = [link for link in links if link['html'] is not None]

		return {'links' : links,
				'me' : model_to_dict(me),
				'post_form' : self.PostForm(),
				'comment_form' : self.CommentForm()}

def home(request):
	return TimelineView.as_view(just_me = True)(request)

def timeline(request):
	return TimelineView.as_view()(request)

def add_content_link(friend_address, friend_port, content_text, parent_id):
	"""Adds content 'content_text' to a html file on the local server 
	and creates a row in the Content model which refers to it. Then
	the friend is sent a link to this content."""
	me = Friend.objects.get(name=o2m.settings.ME)
	variables = {
		'content_text': content_text
	}
	content_add_response = get_from_friend('/content/{0}'.format(content_id), me, me, method='POST', variables = variables)

	content_id = json.loads(content_add_response.read())['content_id']

	friend = Friend.objects.get(address = friend_address, port = friend_port)

	return get_from_friend('/node/{0}'.format(parent_id), friend , me, method='POST', variables = {'content_id': content_id})


def add_content(request):
	"""Adds content to this server whilst also sending a new link to the friend
	specified in the POST variables
	"""
	print '(Client)',request.POST
	friend_address = request.POST['friend_address']
	friend_port = request.POST['friend_port']
	content_text = request.POST['content_text']
	parent_id = request.POST['content_id']

	resp = add_content_link(friend_address, friend_port, content_text, parent_id)
	
	if resp.status == 200:
		print "Success"
		return redirect('/o2m/timeline')
	else:
		print "Failure"
		return HttpResponse(resp.read())
		#return redirect('/o2m/timeline?error=Linking+Error')


