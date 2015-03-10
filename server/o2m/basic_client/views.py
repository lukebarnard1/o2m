

from django.http import HttpResponse
from basic_server.models import Link, Content, Friend
import httplib, urllib
import json

def get_from_friend(source_address, me):
	try:
		con = httplib.HTTPConnection(me.address, me.port)
		con.request('GET', source_address + '?' + urllib.urlencode({'username':me.name, 'password': me.password}))
		resp = con.getresponse()

		#Retrieve new password for request next time
		new_password = resp.getheader('np')

		if new_password is not None:
			me.password = new_password
			me.save()
	finally:
		con.close()
	return resp

def render_links(tree, me):
	html = '<li>'
	content_link = '/content/{2}'.format(tree['friend']['address'], tree['friend']['port'], tree['content']) 
	resp = get_from_friend(content_link, me)

	content_type = resp.getheader('Content-Type')

	if content_type == 'html':
		html += resp.read()
	elif content_type == 'jpg':
		html += '<img src="{0}" width="100">'.format(content_link)

	html += '<ul>'
	for child in tree['children']:
		html += render_links(child, me)
	html += '</ul>'
	html += '</li>'
	return html

def home(request):
	# The first Friend is "the owner, so use it to access the server"
	me = Friend.objects.filter()[0]

	source_address = '/posts'
	html = ''
	try:
		resp = get_from_friend(source_address, me)
		content = resp.read()

		html += '<h1>Home</h1>'

		html += render_links(json.loads(content), me)

	except Exception as e:
		html += 'Failed to get JSON (from '+ me.name + '): ' + str(resp.status) + ' - ' + str(resp.reason) + ' ' + str(e) + '<br>'
		html += 'Response text: ' + content


	return HttpResponse(html)