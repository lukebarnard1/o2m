

import httplib, urllib
import json
import dateutil.parser

from django import forms
from django.http import HttpResponse
from django.views.generic import TemplateView
from basic_server.models import Link, Content, Friend
from django.shortcuts import redirect
import o2m
import random
import string

def random_content_name():
	return "".join([random.choice(string.ascii_letters + string.digits + "-") for i in xrange(32)])

def get_authenticated_link(source_address, me, friend):
	return source_address + '?' + urllib.urlencode({'username':me.name, 'password': friend.password})

def get_from_friend(source_address, friend , me, method = 'GET', variables = {}):
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

def render_links(tree, friend, me):
	content_link = '/content/{0}'.format(tree['content']) 
	try:
		resp = get_from_friend(content_link, friend, me)
	except:
		print "Something went wrong..."

	content_type = resp.getheader('Content-Type')
	html = '<li>'
	html += '<ul><li>' + friend.name + '</li>'
	if content_type == 'text/html':
		html += '<li>' + resp.read() + '</li></ul>'
	elif content_type.startswith('image'):
		"""
		TODO: Fix with caching the image


		"""
		# This should not be used because the new password gets given to the browser, which does nothing with it!
		# html += '<img src="{0}" width="100">'.format(get_authenticated_link(content_link, me, friend))
		html += '<img src="{0}" width="100">'.format('https://www.google.ch/images/srpr/logo11w.png')

	html += '<ul>'
	for child in tree['children']:
		html += render_links(child, friend, me)
	html += '</ul>'
	html += '</li>'
	return html

def home(request):
	# The first Friend is "the owner, so use it to access the server"
	me = Friend.objects.filter()[0]

	source_address = '/posts'
	html = ''
	try:
		resp = get_from_friend(source_address, me, me)
		content = resp.read()

		html += '<h1>Home</h1>'

		html += render_links(json.loads(content), me, me)

	except Exception as e:
		html += 'Failed to get JSON (from '+ me.name + '): ' + str(resp.status) + ' - ' + str(resp.reason) + ' ' + str(e) + '<br>'
		html += 'Response text: ' + content

	return HttpResponse(html)

class TimelineView(TemplateView):
	template_name = "timeline.html"


	class CommentForm(forms.Form):
	    content_text = forms.CharField(label='Comment', max_length=128)

	def get_context_data(self, **kwargs):

		me = Friend.objects.filter()[0]
		print "(Client)Me:",me

		source_address = '/timeline'

		friends = Friend.objects.filter()#[1:]

		timeline = []

		for friend in friends:
			resp = get_from_friend(source_address, friend, me)
			print "(Client)Got {0} '{1}' whilst accessing {2}".format(resp.status, resp.reason, friend.name)
			if resp.status == 200: 
				content = resp.read()
				timeline.extend(json.loads(content))
			else:
				pass

		def newest_first(a, b):
			t1 = dateutil.parser.parse(a['creation_time'])
			t2 = dateutil.parser.parse(b['creation_time'])
			return int((t1 - t2).total_seconds())

		sorted(timeline, cmp=newest_first)
		timeline.sort()

		def get_children_indented(children, level = 0):
			flat_children = []
			print "(Client)Level:" ,level

			for link in children:
				link['level'] = range(level)
				flat_children.append(link)
				if len(link['children']):
					flat_children.extend(get_children_indented(link['children'], level = level + 1))

			return flat_children

		links = get_children_indented(timeline)

		for link in links:
			friend = Friend.objects.get(address = link['friend']['address'], port = link['friend']['port'])
			link['html'] = link_to_html(link, friend, me)

		return {'links' : links,
				'comment_form' : self.CommentForm()}


def timeline(request):
	return TimelineView.as_view()(request)

def add_content_link(friend_address, friend_port, content_text, parent_id):
	"""Adds content 'content_text' to a html file on the local server 
	and creates a row in the Content model which refers to it. Then
	the friend is sent a link to this content."""
	me = Friend.objects.filter()[0]

	content_file_name = o2m.settings.O2M_BASE + '/' + random_content_name() + '.html'

	try:
		f = open(content_file_name, 'w')
		f.write(content_text)
	finally:
		f.close()

	content = Content.objects.create(file_path = content_file_name)
	content.save()

	content_id = content.pk

	friend = Friend.objects.get(address = friend_address, port = friend_port)

	return get_from_friend('/node/{0}'.format(parent_id), friend , me, method='POST', variables = {'content_id': content_id})


def add_content(request):
	"""Adds content to this server whilst also sending a new link to the friend
	specified in the POST variables
	"""
	print '(Client)'+request.POST
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
		return redirect('/o2m/timeline?error=Linking+Error')


