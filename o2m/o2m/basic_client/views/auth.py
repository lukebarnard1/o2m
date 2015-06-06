
from django.views.generic import View
from django.shortcuts import redirect

class AuthenticatedView(View):

	def dispatch(self, request, *args, **kwargs):
		self.username = request.user.username
		self.session_key = request.session.session_key

		print '(Client)Logged in as %s with session %s' % (self.username, request.session.session_key)

		if self.username == '':
			print '(Client)User needs to login'
			return redirect('/o2m/login')

		return super(AuthenticatedView, self).dispatch(request, *args, **kwargs)