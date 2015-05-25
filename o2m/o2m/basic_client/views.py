

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

def get_authenticated_link(source_address, me, friend):
	return source_address# + '?' + urllib.urlencode({'username':me.name, 'password': friend.password})

def get_from_friend(source_address, friend , me, method = 'GET', variables = {}):
	address = friend.address
	if address == '127.0.0.1':
		import socket
		hostname = socket.gethostname()
		address = socket.gethostbyname(hostname)
		print '(Client)Converting 127.0.0.1 to %s' % address

	print "(Client)Logging into {0} as {1} to do {2} with {3} with URL {5}:{6}{4} ".format(friend, me, method, variables, source_address, address, friend.port)
	
	con = httplib2.Http('cache')

	url = 'http://%s:%s%s' % (address, friend.port, get_authenticated_link(source_address, me, friend))

	headers = {
		#This should be base64 encoded
		"Authorization": 'Basic %s:%s' % (me.name, friend.password),
		"Content-Type": "application/x-www-form-urlencoded",
		"Accept": "text/plain"}

	response_headers, content = con.request(url, method, headers = headers, body=urllib.urlencode(variables))

	# If there's a new password, update it for this friend
	if 'np' in response_headers.keys():
		friend.password = response_headers['np']
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

class AuthenticatedView(View):

	def dispatch(self, request, *args, **kwargs):
		self.username = request.user.username
		self.session_key = request.session.session_key

		print '(Client)Logged in as %s with session %s' % (self.username, request.session.session_key)

		if self.username == '':
			print '(Client)User needs to login'
			return redirect('/o2m/login')

		return super(AuthenticatedView, self).dispatch(request, *args, **kwargs)

class TimelineView(AuthenticatedView, TemplateView):
	template_name = "timeline.html"

	#Whether the posts are mine or my friends as well
	just_me = False

	#Taken from the request
	username = None

	class CommentForm(forms.Form):
		content_text = forms.CharField(label='Comment', max_length=128)
	
	class PostForm(forms.Form):
		content_text = forms.CharField(label='Post')

	class ChangeUsernameForm(forms.Form):
		username = forms.CharField(label='Username')


	def get_friends_included(self):
		if self.just_me:
			friends = [Friend.objects.get(name=self.username)]
		else:
			friends = Friend.objects.filter()
		return friends

	def get_context_data(self, **kwargs):
		me = Friend.objects.get(name=self.username)

		source_address = '/timeline'

		friends = self.get_friends_included()

		timeline = []

		should_change_username = False

		def assign_links_address(links):
			for link in links:
				link['address'] = friend.address
				link['port'] = friend.port
				link['link_friend'] = friend
				if len(link['children']):
					assign_links_address(link['children'])
			return links

		for friend in friends:
			response_headers = None
			try:
				response_headers, content = get_from_friend(source_address, friend, me)
			except Exception as e:
				print "(Client)Loading timeline data from {0} failed: {1}".format(friend.name, e)
			
			if response_headers is not None :
				if response_headers['status'] == '200':
					links_from_friend = json.loads(content)

					links_from_friend = assign_links_address(links_from_friend)

					timeline.extend(links_from_friend)
				# elif resp.reason == 'Need to change username' and friend == me:
				elif friend == me:
					should_change_username = True
			else:
				print "(Client)There was no response from {0}".format(friend.name)

		if should_change_username:
			self.template_name = "change_username.html"
			return {
				'change_username_form': self.ChangeUsernameForm()
			}

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
				link['level'] = range(level)
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

		me_dict = model_to_dict(me)

		return {'links' : links,
				'me' : me_dict,
				'post_form' : self.PostForm(),
				'comment_form' : self.CommentForm()}

def home(request):
	return TimelineView.as_view(just_me = True)(request)

def timeline(request):
	return TimelineView.as_view()(request)

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
		print "Success"
		return redirect('/o2m/timeline')
	else:
		print "Failure"
		return HttpResponse(content)
		#return redirect('/o2m/timeline?error={0}'.format(resp.reason))

def delete_content(request):
	"""Deletes content from the server belonging to 'me'
	"""
	me = Friend.objects.get(name=request.user.username)
	content_id = request.POST['content_id']

	response_headers, content = get_from_friend('/content/{0}'.format(content_id), me, me, method = 'DELETE')

	if response_headers['status'] == '200':
		print "Success"
		return redirect('/o2m/timeline')
	else:
		print "Failure"
		return HttpResponse(content)
		#return redirect('/o2m/timeline?error={0}'.format(resp.reason))

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
		print "Success"
		return redirect('/o2m/timeline')
	else:
		print "Failure"
		return HttpResponse(content)
		#return redirect('/o2m/timeline?error={0}'.format(resp.reason))

class NotificationView(AuthenticatedView, TemplateView):
	template_name = "notifications.html"

	def get_context_data(self, **kwargs):
		me = Friend.objects.get(name=self.username)
		print "(Client)Me:",me

		source_address = '/notifications/'

		response_headers = None

		try:
			response_headers, content = get_from_friend(source_address, me, me)
		except Exception as e:
			print "Loading notifications data from {0} failed: {1}".format(me.name, e)

		if response_headers is not None:
			if response_headers['status'] == '200':
				notifications = json.loads(content)

				return {'notifications' : notifications,
						'me' : model_to_dict(me)}

def notifications(request):
	return NotificationView.as_view()(request)


class FriendView(TimelineView):
	
	friend_name = None
	friend_ip = None
	friend_port = None

	def get_friends_included(self):
		fs = Friend.objects.filter(name=self.friend_name)

		if len(fs) == 0:
			f = None
		else:
			f = fs[0]

		if f is None:
			if not ((self.friend_ip is None) or (self.friend_port is None)):
				existing = Friend.objects.filter(name = self.friend_name, address = self.friend_ip, port = self.friend_port)
				already_exists = len(existing) > 0

				if not already_exists:
					new_friend = Friend.objects.create(name = self.friend_name, address = self.friend_ip, port = self.friend_port, password = 'NOTFRIENDS')
					new_friend.save()
					self.friend = new_friend
					return [new_friend]
				else:
					self.friend = existing[0]
					return [existing[0]]
			raise Exception('Friend unknown, supply ip and port to non_friend endpoint')
		else:
			self.friend = f
			return [f]

	def get_context_data(self, **kwargs):
		context = super(FriendView, self).get_context_data(**kwargs)

		self.friend.user_photo_content_id = 1

		context.update(friend = self.friend, non_friend = (self.friend.password == 'NOTFRIENDS'), request_sent = (self.friend.password == 'REQUESTSENT'), request_received = (self.friend.password == 'REQUESTRECEIVED'))

		return context

def friend(request, **kwargs):
	return FriendView.as_view(**kwargs)(request)

def to_django_response(response_headers, content):
	resp = HttpResponse(content)
	for k,v in response_headers.iteritems():
		try:
			resp[k] = v
		except Exception as e:
			print '(Client[views.to_django_response])Ignoring %s = %s' % (k, v)
	return resp

def friend_content(request, friend_name, content_id):

	me = Friend.objects.get(name=request.user.username)
	friend = Friend.objects.get(name=friend_name)

	source_address = '/content/%s' % content_id
	
	response_headers, content = get_from_friend(source_address, friend , me)
	return to_django_response(response_headers, content)

def non_friend(request, **kwargs):
	return FriendView.as_view(**kwargs)(request)

def add_friend(request, friend_name, friend_ip, friend_port):
	print '(Client)Adding friend:'
	print '\tfriend_name: %s' % friend_name
	print '\tfriend_ip: %s' % friend_ip
	print '\tfriend_port: %s' % friend_port
	me = Friend.objects.get(name=request.user.username)

	friend = Friend.objects.get(name = friend_name, address = friend_ip, port = friend_port)

	if friend.password == 'REQUESTRECEIVED':
		new_user = User.objects.create_user(friend.name, password='REQUESTSENT')
		new_user.save()

	friend.send_notification(me, 'Friend request', -1, me.name)
	friend.password = 'REQUESTSENT'
	friend.save()

	return redirect('/o2m/friend/%s' % friend.name)

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

class LoginView(TemplateView):
	template_name = "login.html"

	class LoginForm(forms.Form):
		username = forms.CharField(label='Username', max_length=128)
		password = forms.CharField(label='Password', max_length=32, widget=forms.PasswordInput)

	def get_context_data(self, **kwargs):
		return {'login_form': self.LoginForm()}

def login_view(request, **kwargs):
	return LoginView.as_view(**kwargs)(request)

from django.contrib.auth import authenticate, login
def login_user(request):
	username = request.POST['username']
	password = request.POST['password']
	print '(Client)Authenticating %s %s' % (username, password)
	user = authenticate(username=username, password=password) 
	if user is not None:
		if user.is_active:
			login(request, user)
			return redirect('/o2m/timeline')
		else:
			return HttpResponse('Not Registered (not active)')
	else:
		return HttpResponse('Not Registered')

class ContentAddView(AuthenticatedView, TemplateView):
	template_name = "content_add.html"

	class ContentAddForm(forms.Form):
		"""A simple form to add a file into the flat-storage of all
		contents belonging to this user.
		"""
		file = forms.FileField()

	def get_context_data(self, **kwargs):
		return {'content_add_form': self.ContentAddForm()}

# As suggested by the Django documentation here: https://docs.djangoproject.com/en/1.8/topics/http/file-uploads/
def handle_uploaded_file(f):
	with open('client_temp/%s' % f.name, 'wb+') as destination:
		destination.write(f.read())

def content_add_view(request, **kwargs):
	return ContentAddView.as_view(**kwargs)(request)
