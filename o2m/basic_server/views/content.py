
import json
from django.http import HttpResponse
import o2m
from ..models import Content
from auth import AuthenticatedView

class ContentView(AuthenticatedView):

	def must_be_owner(self, request):
		"""You must always be the owner to add or delete content"""
		return request.method in ('POST', 'DELETE')

	def get(self, request):
		try:
			resp = Content.objects.get(pk=self.content_id).get_http_response()
		except Exception as e:
			print "(Server){0}".format(e)
			resp = HttpResponse('Could not find that content')
			resp.reason_phrase = 'Could not find that content'
			resp.status_code = 404
		return resp

	def post(self, request):
		content_text = request.POST['content_text']
		content_id = self.content_id
		content_file_name = o2m.settings.O2M_BASE + '/' + content_id + '.html'

		print '(Server)Using content_id {0} for content filename (but not for the actual id yet)'.format(content_id)

		try:
			f = open(content_file_name, 'w')
			f.write(content_text)
		except Exception as e:
			print "(Server){0}".format(e)
		finally:
			f.close()

		content = Content.objects.create(file_path = content_file_name)
		content.save()

		return HttpResponse(json.dumps({'content_id' : content.pk}))

	def delete(self, request):
		try:
			content = Content.objects.get(pk = self.content_id)
			content.delete()

			return HttpResponse('Content deleted')
		except Exception as e:
			print "(Server){0}".format(e)
			resp = HttpResponse('Could not delete that content')
			resp.reason_phrase = 'Could not delete that content'
			resp.status_code = 404
			return resp