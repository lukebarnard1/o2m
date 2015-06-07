from django.db import models
from django.forms.models import model_to_dict
import o2m.settings
import mptt.models
from mptt.fields import TreeForeignKey
import os
import httplib
import urllib
import json,mimetypes
from datetime import datetime
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.db.models.signals import post_delete as post_delete_signal
from django.dispatch import receiver

# Create your models here.


def file_path_to_media(file_path):
	return o2m.settings.MEDIA_URL + file_path[len(o2m.settings.O2M_BASE) + 1:]

def read_file(file_path):
	try:
		# print 'o2m.settings.MEDIA_ROOT={0}'.format(o2m.settings.MEDIA_ROOT)
		# print 'o2m.settings.MEDIA_URL={0}'.format(o2m.settings.MEDIA_URL)
		# print 'file_path={0}'.format(file_path)
		# print 'file_path[len(o2m.settings.MEDIA_URL):]={0}'.format(file_path[len(o2m.settings.MEDIA_URL):])
		f = open(os.path.join(o2m.settings.MEDIA_ROOT,file_path[len(o2m.settings.MEDIA_URL):]), 'r')
	except IOError as e:
		return str(e)
	try:
		text = f.read()
		return text
	except IOError as e:
		return 'Failed to read text file at ' + file_path


class Friend(models.Model):
	name = models.CharField(max_length=128)
	address = models.GenericIPAddressField()
	port = models.IntegerField(default=8000)
	password = models.CharField(max_length=32)
	photo_content_id = models.IntegerField(default=1)

	def get_authenticated_link(self, source_address, me):
		return source_address + '?' + urllib.urlencode({'username':me.name, 'password': self.password})

	def get_from_friend(self, source_address, me, method = 'GET', variables = {}):
		print "(Server)Logging into {0} as {1} to do {2} with {3} with URL {5}:{6}{4} ".format(self, me, method, variables, source_address, self.address, self.port)
		try:
			con = httplib.HTTPConnection(self.address, self.port)
			con.request(method, self.get_authenticated_link(source_address, me), urllib.urlencode(variables) ,{"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"})
			resp = con.getresponse()

			#Retrieve new password for request next time
			new_password = resp.getheader('np')

			if new_password is not None:
				self.password = new_password
				self.save()
			print "(Client){3}ing {0} has given the new password {1} to access {2}".format(source_address, self.password, self.name, method)
		finally:
			con.close()
		return resp

	def send_notification(self, me, notification_type, obj_id, obj_creator):
		return self.get_from_friend('/notifications/', me, method='POST',\
			variables={'notification_type':notification_type, 'obj_id':obj_id, 'obj_creator':obj_creator})

	def __str__(self):
		return "{0}@{1}".format(self.name, self.address)

class Content(models.Model):
	file_path = models.FilePathField(path=o2m.settings.O2M_CONTENT_BASE, recursive=True)
	integer = models.IntegerField(default=0) # Non-descript to allow variations

	def get_mime_type(self):
		return mimetypes.guess_type(self.file_path)[0]

	def get_http_response(self):
		"""Returns a HttpResponse that will return the file of this content.
		"""
		import datetime, time
		from wsgiref.handlers import format_date_time
		expires = datetime.timedelta(hours=1) + datetime.datetime.now()

		r = HttpResponse(FileWrapper(open(self.file_path,"rb")), content_type=self.get_mime_type())
		r['Expires'] = format_date_time(time.mktime(expires.timetuple()))

		return r

	@receiver(post_delete_signal)
	def post_delete(sender, **kwargs):
		if sender == Content:
			self, signal, using = tuple(kwargs.values())
			try:
				os.remove(self.file_path)
				return True
			except:
				print 'Failed to remove associated content file at {0}'.format(self.file_path)
				return False

	def __str__(self):
		return "Content[{1}] at {0}".format(self.file_path, self.id)

class Link(mptt.models.MPTTModel):
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
	friend = models.ForeignKey(Friend) # (Could be yourself)
	creation_time = models.DateTimeField(auto_now_add=True)
	content = models.BigIntegerField() # (Could be your own)

	def dict_for_node(self):
		result = model_to_dict(self)
		result['creation_time'] = self.creation_time.__str__()

		result['friend'] = model_to_dict(Friend.objects.get(pk=result['friend']))
		
		del result['friend']['password']
		del result['parent']

		result['children'] = [child.dict_for_node() for child in self.get_children().order_by('-creation_time')]

		return result

	def to_json(self):

		json_self = {}
		json_self['friend'] = model_to_dict(self.friend)
		json_self['content'] = self.content

		return json.dumps(json_self)

	def get_content(self):
		"""Returns None if the content is on a friend's computer.

		"""
		if self.friend.id == 1: # This is me
			return Content.objects.get(pk=self.content)
		else:
			return None

	def __str__(self):
		content_text = ''

		if self.friend.id == 1: # This is me
			try:
				content_text = Content.objects.get(pk=self.content).file_path
			except Exception as e:
				content_text = 'Content could not be found'
		else:
			content_text = 'The file is on another friend\'s computer'

		return "Link {0}: Content {1}".format(self.friend.name, content_text)

class NotificationType(models.Model):
	name = models.CharField(max_length=32)
	obj_type = models.CharField(max_length=32)
	title = models.CharField(max_length=64)

	def __str__(self):
		return 'NotificationType: %s about %s' % (self.name, self.obj_type)

class Notification(models.Model):
	notification_type = models.ForeignKey(NotificationType)

	# The server that obj exists on
	obj_server = models.ForeignKey(Friend, related_name='server')
	# The one who generated the notification or the creator of the object it refers to
	obj_creator = models.ForeignKey(Friend, related_name='creator')
	# The ID of the object on the server
	obj_id = models.BigIntegerField()
