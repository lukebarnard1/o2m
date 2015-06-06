
import socket
import httplib2,urllib
import dateutil.parser
from datetime import datetime, timedelta
import pytz

def get_from_friend(source_address, friend , me, method = 'GET', variables = {}):
	address = friend.address
	if address == '127.0.0.1':
		hostname = socket.gethostname()
		address = socket.gethostbyname(hostname)
		print '(Client)Converting 127.0.0.1 to %s' % address

	
	con = httplib2.Http('cache')

	url = 'http://%s:%s%s' % (address, friend.port, source_address)

	headers = {
		#This should be base64 encoded
		"Authorization": 'Basic %s:%s' % (me.name, friend.password),
		"Content-Type": "application/x-www-form-urlencoded",
		"Accept": "text/plain"}

	utc=pytz.UTC
	
	d = datetime.now(utc) - timedelta(seconds = 1)
	response_headers, content = con.request(url, method, headers = headers, body=urllib.urlencode(variables))

	# Was this cached? Did the response get sent more than a second ago?
	was_cached = dateutil.parser.parse(response_headers['date']) < d

	if not was_cached:
		print "(Client)Logged into {0} as {1} to do {2} with {3} with URL {5}:{6}{4} ".format(friend.name, me.name, method, variables, source_address, address, friend.port)
		print "\t Got %s" % response_headers['status']

	# If there's a new password, update it for this friend
	if not was_cached and 'np' in response_headers.keys():
		friend.password = response_headers['np']
		# print '\t Password for %s now %s'% (friend.name, friend.password)
		friend.save()	
	return response_headers, content

def link_to_html(link, friend, me):
	content_link = '/content/{0}'.format(link['content'])

	response_headers, content = get_from_friend(content_link, friend, me)

	content_type = response_headers['content-type']

	if response_headers['status'] == '200':
		if content_type == 'text/html':
			return content
		elif content_type.startswith('image'):
			return '<img src="http://%s:%s/o2m/friend/%s/content/%s" width="100">' % (me.address, me.port, friend.name, link['content'])
		else: 
			return 'Error fetching content: unknown content type'
	else:
		return 'Error fetching content: {0} '.format(response_headers['status'])



import httplib2, urllib
import json
import dateutil.parser

from django import forms
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from o2m.basic_server.models import Link, Content, Friend
from django.forms.models import model_to_dict
from django.shortcuts import redirect
import o2m, o2m.settings
import random
import string
from datetime import datetime, timedelta
import pytz
import socket


def add_content_link(me, friend_address, friend_port, content_text, parent_id):
	"""Adds content 'content_text' to a html file on the local server 
	and creates a row in the Content model which refers to it. Then
	the friend is sent a link to this content."""

	me = Friend.objects.get(name=me)
	variables = {
		'content_text': content_text
	}

	response_headers, content = get_from_friend('/content/', me, me, method='POST', variables = variables)

	if response_headers['status'] == '200':
		content_id = json.loads(content)['content_id']

		friend = Friend.objects.get(address = friend_address, port = friend_port)

		return get_from_friend('/node/{0}'.format(parent_id), friend , me, method='POST', variables = {'content_id': content_id})
	else:
		return response_headers, content


def add_linked_content(request):
	"""Adds content to the server belonging to 'me' whilst also sending a new link to the friend
	specified in the POST variables
	"""
	friend_address = request.POST['friend_address']
	friend_port = request.POST['friend_port']
	content_text = request.POST['content_text']
	parent_id = request.POST['content_id']

	me = request.user.username

	response_headers, content = add_content_link(me, friend_address, friend_port, content_text, parent_id)
	
	if response_headers['status'] == '200':
		print "(Client)Success"
		return redirect('/o2m/timeline')
	else:
		print "(Client)Failure"
		return redirect('/o2m/timeline?error={0}'.format(response_headers))

def delete_content(request):
	"""Deletes content from the server belonging to 'me'
	"""
	me = Friend.objects.get(name=request.user.username)
	content_id = request.POST['content_id']

	response_headers, content = get_from_friend('/content/{0}'.format(content_id), me, me, method = 'DELETE')

	if response_headers['status'] == '200':
		print "(Client)Success"
		return redirect('/o2m/timeline')
	else:
		print "(Client)Failure"
		return redirect('/o2m/timeline?error={0}'.format(response_headers))

def delete_link(request):
	"""Deletes link belonging to a friend (who could be 'me')

	This requires the POST variable 'content_id' to be set to the 
	content that this link refers to. The content may have been 
	deleted already, but it is also not necessary for it to have
	been deleted.
	"""
	me = Friend.objects.get(name=request.user.username)
	
	content_id = request.POST['content_id']
	friend_id = request.POST['friend_id']

	friend = Friend.objects.get(pk=friend_id)

	response_headers, content = get_from_friend('/node/{0}'.format(content_id), friend, me, method = 'DELETE')

	if response_headers['status'] == '200':
		print "(Client)Success"
		return redirect('/o2m/timeline')
	else:
		print "(Client)Failure"
		return redirect('/o2m/timeline?error={0}'.format(response_headers))



from django.contrib.auth.models import User
from django.contrib.auth import logout
# This should be in the SERVER
def username(request):
	new_username = request.POST['username']

	# Update Friends table

	me = Friend.objects.get(name=o2m.settings.DEFAULT_USERNAME)
	me.name = new_username

	# Set the IP to the network address
	import socket
	hostname = socket.gethostname()
	me.address = socket.gethostbyname(hostname)
	me.save()

	user = User.objects.get(username=o2m.settings.DEFAULT_USERNAME)
	user.username = new_username
	user.save()

	logout(request)

	return redirect('/o2m/login')
