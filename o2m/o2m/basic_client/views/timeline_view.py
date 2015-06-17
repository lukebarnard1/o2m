from auth import AuthenticatedView
from django.views.generic import TemplateView
from django import forms
from django.forms.models import model_to_dict
from o2m.basic_server.models import Friend
from o2m.basic_client.views import get_from_friend, link_to_html, get_friends
import json
import dateutil.parser

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
		me = Friend.objects.get(name=self.username)
		if self.just_me:
			friends = [me]
		else:
			friends = Friend.objects.exclude(password='NOTFRIENDS')
		return friends

	def get_context_data(self, **kwargs):
		me = Friend.objects.get(name=self.username)

		source_address = '/timeline'

		friends = self.get_friends_included()
		print '(Client)Friends acquired'
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

