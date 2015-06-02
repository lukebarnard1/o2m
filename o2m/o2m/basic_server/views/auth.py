
import random, string
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth import authenticate, login
import o2m
from o2m.basic_server.models import Friend

def random_password():
	return "".join([random.choice(string.ascii_letters + string.digits + ".-") for i in xrange(32)])


class AuthenticatedView(View):

	content_id = 1
	limit = 3

	def must_be_owner(self, request):
		"""True if the username and password should be the owner
		of the server.
		"""
		return False

	def dispatch(self, request, *args, **kwargs):
		response = HttpResponse()

		if not request.user.is_authenticated():
			try:
				auth = request.META['HTTP_AUTHORIZATION']
				import re
				m = re.search('Basic ([^\:]+):(.+)', auth)

				username = m.group(1)
				password = m.group(2)

				print '(Server)Authenticating ' + username + ' with pw ' + password
				user = authenticate(username=username, password=password)
				if user is not None:
					print '(Server)User authenticated as ' + username
					if user.is_active:
						print '(Server)Logging in...'
						login(request, user)
					else:
						response.reason_phrase = 'You are not my friend anymore'
						response.status_code = 401
						return response
				else:
					response.reason_phrase = 'You are not my friend or that password was wrong'
					response.status_code = 401
					return response
			except Exception as e:
				raise e
				response.reason_phrase = 'Unauthorized'
				response.status_code = 401
				print 'Sending back Unauthorized'
				return response
		else:
			username = request.user.username
			user = request.user

		if username == o2m.settings.DEFAULT_USERNAME:
			change_username_response = HttpResponse('Need to change username')
			change_username_response.reason_phrase = 'Need to change username'
			change_username_response.status_code = 401
			return change_username_response

		possible_friends = Friend.objects.filter(name=username)
		if len(possible_friends):
			friend = possible_friends[0]
			print '(Server)Updating Friend IP'
			from ipware.ip import get_ip
			address = get_ip(request)
			print '%s\'s new address is %s' %(friend.name, friend.address)
			friend.address = address
			friend.save()

		if not self.must_be_owner(request) or user.is_staff:
			print '(Server)Dispatching...'
			response = super(AuthenticatedView, self).dispatch(request, *args, **kwargs)

			if not user.is_staff:
				new_password = random_password()

				user.set_password(new_password)

				# print '\t Password for %s now %s'% (user.username, new_password)
				user.save()

				response['np'] = new_password
		else:
			response.reason_phrase = 'Only the owner can do that'
			response.status_code = 401

		
		# Display simple content to display error for slightly easier debug
		if response.status_code != 200: response.content += str(response.status_code) + '  ' + str(response.reason_phrase) 

		return response