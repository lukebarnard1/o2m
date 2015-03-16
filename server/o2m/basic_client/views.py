

from django.http import HttpResponse
from basic_server.models import Link, Content, Friend
import httplib, urllib
import json

def get_authenticated_link(source_address, me, friend):
	return source_address + '?' + urllib.urlencode({'username':me.name, 'password': friend.password})

def get_from_friend(source_address, friend , me):
	try:
		con = httplib.HTTPConnection(friend.address, friend.port)
		con.request('GET', get_authenticated_link(source_address, me, friend))
		resp = con.getresponse()

		#Retrieve new password for request next time
		new_password = resp.getheader('np')

		if new_password is not None:
			friend.password = new_password
			friend.save()
		print "Getting {0} has given the new password {1}".format(source_address, friend.password)
	finally:
		con.close()
	return resp

def render_links(tree, friend, me):
	content_link = '/content/{2}'.format(tree['friend']['address'], tree['friend']['port'], tree['content']) 
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
		html += '<img src="{0}" width="100">'.format(get_authenticated_link(content_link, me, friend))

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


def timeline(request):
	me = Friend.objects.filter()[0]

	source_address = '/timeline'

	friends = Friend.objects.filter()#[1:]
	html = '<h1>Timeline</h1>'

	timeline = []

	for friend in friends:
		resp = get_from_friend(source_address, friend, me)
		print "Got {0} '{1}' whilst accessing {2}".format(resp.status, resp.reason, friend.name)
		if resp.status == 200: 
			content = resp.read()
			timeline.extend(json.loads(content))
		else:
			pass# return HttpResponse(resp.read())

	def newest_first(a,b):
		print a['creation_time']
		print b['creation_time']
		return 1

	sorted(timeline, cmp=newest_first)
	timeline.sort()

	for post in timeline:
		html += render_links(post, friend, me)

	return HttpResponse(html)