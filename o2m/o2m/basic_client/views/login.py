
from django.views.generic import TemplateView
from django import forms
from django.http import HttpResponse

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
			resp = HttpResponse('Successful login!')
			resp.status_code = 200
			return resp
		else:
			resp = HttpResponse('Not Registered (not active)')
			resp.status_code = 500
			return resp
	else:
		resp = HttpResponse('Not Registered')
		resp.status_code = 500
		return resp