
import random, string
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth import authenticate, login
import o2m

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

		try:
			username = request.GET['username']
			password = request.GET['password']

		except MultiValueDictKeyError as e:
			response.reason_phrase = 'Give me username and password'
			response.status_code = 401
			return response

		if username == o2m.settings.DEFAULT_USERNAME:
			change_username_response = HttpResponse('Need to change username')
			change_username_response.reason_phrase = 'Need to change username'
			change_username_response.status_code = 401
			return change_username_response

		print '(Server)Authenticating ' + username + ' with pw ' + password
		user = authenticate(username=username, password=password)
		if user is not None:
			print '(Server)User authenticated as ' + username
			if user.is_active:
				print '(Server)Logging in...'
				login(request, user)

				if not self.must_be_owner(request) or user.is_staff:
					print '(Server)Dispatching...'
					response = super(AuthenticatedView, self).dispatch(request, *args, **kwargs)

					if not user.is_staff:
						new_password = random_password()

						user.set_password(new_password)
						user.save()

						response['np'] = new_password
				else:
					response.reason_phrase = 'Only the owner can do that'
					response.status_code = 401
			else:
				response.reason_phrase = 'You are not my friend anymore'
				response.status_code = 401

		else:
			response.reason_phrase = 'You are not my friend or that password was wrong'
			response.status_code = 401
		
		# Display simple content to display error for slightly easier debug
		if response.status_code != 200: response.content += str(response.status_code) + '  ' + str(response.reason_phrase) 

		return response