

import httplib, urllib
import json
import dateutil.parser

from django import forms
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from basic_server.models import Link, Content, Friend
from django.forms.models import model_to_dict
from django.shortcuts import redirect
import o2m, o2m.settings
import random
import string

def random_content_name():
	return "".join([random.choice(string.digits) for i in xrange(8)])

def get_authenticated_link(source_address, me, friend):
	return source_address + '?' + urllib.urlencode({'username':me.name, 'password': friend.password})

def get_from_friend(source_address, friend , me, method = 'GET', variables = {}):
	address = friend.address
	if address == '127.0.0.1':
		import socket
		hostname = socket.gethostname()
		address = socket.gethostbyname(hostname)
		print '(Client)Converting 127.0.0.1 to %s' % address

	print "(Client)Logging into {0} as {1} to do {2} with {3} with URL {5}:{6}{4} ".format(friend, me, method, variables, source_address, address, friend.port)
	try:
		con = httplib.HTTPConnection(address, friend.port)
		con.request(method, get_authenticated_link(source_address, me, friend), urllib.urlencode(variables) ,{"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"})
		resp = con.getresponse()

		#Retrieve new password for request next time
		new_password = resp.getheader('np')

		if new_password is not None:
			friend.password = new_password
			friend.save()
		# print "(Client){3}ing {0} has given the new password {1} to access {2}".format(source_address, friend.password, friend.name, method)
	finally:
		con.close()
	return resp

def link_to_html(link, friend, me):
	content_link = '/content/{0}'.format(link['content'])

	resp = get_from_friend(content_link, friend, me)

	content_type = resp.getheader('Content-Type')

	"""
	TODO: Should this be clientside? Yes... 

	- Fetch the contents and store localy
	- Assign a new CachedContent object and store in database
	- Return http response based on newly cached content
	- CachedContents stored in this way should have a TTL before they are fetched again (HTTP Cache header)
	- These cannot be linked to, but if they have timed out then they should be asked for again, otherwise just keep using them
	"""

	if resp.status == 200:
		if content_type == 'text/html':
			return resp.read()
		elif content_type.startswith('image'):
			# This should not be used because the new password gets given to the browser, which does nothing with it!
			# html += '<img src="{0}" width="100">'.format(get_authenticated_link(content_link, me, friend))
			return '<img src="{0}" width="100">'.format('https://www.google.ch/images/srpr/logo11w.png')
	else:
		return 'Error fetching content: {0} {1}'.format(resp.status, resp.reason)

class AuthenticatedView(View):

	def dispatch(self, request, *args, **kwargs):
		self.username = request.user.username

		print '(Client)Logged in as %s' % self.username

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
				if resp.status == 200: 
					content = resp.read()
					links_from_friend = json.loads(content)

					links_from_friend = assign_links_address(links_from_friend)

					timeline.extend(links_from_friend)
				elif resp.reason == 'Need to change username' and friend == me:
					should_change_username = True

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

		return {'links' : links,
				'me' : model_to_dict(me),
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

	content_id = random_content_name()

	content_add_response = get_from_friend('/content/{0}'.format(content_id), me, me, method='POST', variables = variables)

	if content_add_response.status == 200:
		content_id = json.loads(content_add_response.read())['content_id']

		friend = Friend.objects.get(address = friend_address, port = friend_port)

		return get_from_friend('/node/{0}'.format(parent_id), friend , me, method='POST', variables = {'content_id': content_id})
	else:
		return content_add_response


def add_content(request):
	"""Adds content to the server belonging to 'me' whilst also sending a new link to the friend
	specified in the POST variables
	"""
	friend_address = request.POST['friend_address']
	friend_port = request.POST['friend_port']
	content_text = request.POST['content_text']
	parent_id = request.POST['content_id']

	me = request.user.username

	resp = add_content_link(me, friend_address, friend_port, content_text, parent_id)
	
	if resp.status == 200:
		print "Success"
		return redirect('/o2m/timeline')
	else:
		print "Failure"
		return HttpResponse(resp.read())
		#return redirect('/o2m/timeline?error={0}'.format(resp.reason))

def delete_content(request):
	"""Deletes content from the server belonging to 'me'
	"""
	me = Friend.objects.get(name=o2m.settings.ME)
	content_id = request.POST['content_id']

	resp = get_from_friend('/content/{0}'.format(content_id), me, me, method = 'DELETE')

	if resp.status == 200:
		print "Success"
		return redirect('/o2m/timeline')
	else:
		print "Failure"
		return HttpResponse(resp.read())
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

	resp = get_from_friend('/node/{0}'.format(content_id), friend, me, method = 'DELETE')

	if resp.status == 200:
		print "Success"
		return redirect('/o2m/timeline')
	else:
		print "Failure"
		return HttpResponse(resp.read())
		#return redirect('/o2m/timeline?error={0}'.format(resp.reason))

class NotificationView(AuthenticatedView, TemplateView):
	template_name = "notifications.html"

	def get_context_data(self, **kwargs):
		me = Friend.objects.get(name=self.username)
		print "(Client)Me:",me

		source_address = '/notifications/'

		resp = None

		try:
			resp = get_from_friend(source_address, me, me)
		except Exception as e:
			print "Loading notifications data from {0} failed: {1}".format(me.name, e)

		if resp is not None:
			if resp.status == 200:
				notifications = json.loads(resp.read())

				return {'notifications' : notifications,
						'me' : model_to_dict(me)}
			else:
				print resp.reason

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
		context.update(friend = self.friend, non_friend = (self.friend.password == 'NOTFRIENDS'))

		return context

def friend(request, **kwargs):
	return FriendView.as_view(**kwargs)(request)

def non_friend(request, **kwargs):
	return FriendView.as_view(**kwargs)(request)

def add_friend(request, friend_name, friend_ip, friend_port):
	print '(Client)Adding friend:'
	print '\tfriend_name: %s' % friend_name
	print '\tfriend_ip: %s' % friend_ip
	print '\tfriend_port: %s' % friend_port
	me = Friend.objects.get(name=request.user.username)

	friend = Friend.objects.get(name = friend_name, address = friend_ip, port = friend_port)

	friend.send_notification(me, 'Friend request', -1, me.name)

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