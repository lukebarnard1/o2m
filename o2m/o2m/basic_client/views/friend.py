
from timeline_view import TimelineView
from o2m.basic_server.models import Friend

from django.contrib.auth.models import User
from django.shortcuts import redirect

from django.http import HttpResponse
from o2m.basic_client.views import get_from_friend

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
			raise Exception('Friend unknown, supply ip and port')
		elif f.password != 'NOTFRIENDS':
			self.friend = f
			return [f]
		else:
			self.friend = f
			return []

	def get_context_data(self, **kwargs):
		context = super(FriendView, self).get_context_data(**kwargs)

		context.update(friend = self.friend, non_friend = (self.friend.password == 'NOTFRIENDS'), request_sent = (self.friend.password == 'REQUESTSENT'), request_received = (self.friend.password == 'REQUESTRECEIVED'))

		return context

def friend(request, **kwargs):
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