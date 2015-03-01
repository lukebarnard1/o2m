from django.db import models
import o2m.settings
import mptt.models
from mptt.fields import TreeForeignKey
import os
import httplib
import urllib
import json

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
	address = models.IPAddressField()
	port = models.IntegerField(default=8000)
	password = models.CharField(max_length=32)

	def __str__(self):
		return "{0}@{1}".format(self.name, self.address)

class Content(models.Model):
	file_path = models.FilePathField(path=o2m.settings.O2M_BASE, recursive=True)
	creation_time = models.DateTimeField()
	integer = models.IntegerField() # Non-descript to allow variations

	def get_html_representation(self):
		file_path = file_path_to_media(self.file_path)
		file_type = file_path[file_path.rindex('.') + 1:].lower()

		if file_type in ['txt', 'html']:
			text = read_file(file_path)

			if file_type == 'txt':
				return '<p>{0}</p>'.format(escape(text))
			elif file_type == 'html':
				return text

		elif file_type == 'png' or file_type == 'jpg':
			return '<img src="{0}" width="200" alt="{0}">'.format(file_path)

		return 'Unknown file type'

	def __str__(self):
		return "Content at {0}, created {1}".format(self.file_path, self.creation_time)

class Link(mptt.models.MPTTModel):
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
	friend = models.ForeignKey(Friend) # (Could be yourself)
	content = models.BigIntegerField() # (Could be your own)

	def get_content(self):
		"""Returns None if the content is on a friend's computer.

		"""
		if self.friend.id == 1: # This is me
			return Content.objects.get(pk=self.content)
		else:
			return None

	def get_content_from_friend(self):
		friend = self.friend
		html = ''
		print 'Trying to get content from {0} with password {1} and ip {2}'.format(friend.name, friend.password, friend.address)

		source_address = '/content/{0}.json'.format(self.content)
		con = httplib.HTTPConnection(friend.address, friend.port)
		try:
			con.request('GET', source_address + '?' + urllib.urlencode({'username':'Luke Barnard', 'password': friend.password}))
			resp = con.getresponse()

			#Retrieve new password for request next time
			new_password = resp.getheader('np')

			if new_password is not None:
				friend.password = new_password
				friend.save()

			js = resp.read()

			try:
				loaded_content = json.loads(js)

				for name, cls in [('parent', Link),('friend', Friend),('content', Content)]:
					if loaded_content[name]: 
						loaded_content[name] = cls.objects.get(pk=loaded_content[name])
					else:
						loaded_content[name] = None

				print loaded_content

				populated_link = Link(**loaded_content)

				html += '<li class="media"><h4>Linked from {1}:</h4></li>{0}'.format(populated_link.content.get_html_representation(), friend.name)
			except Exception as e:
				html += 'Failed to get JSON: '+ friend.name + str(resp.status) + ' - ' + str(resp.reason) + ' ' + str(e) + '<br>'
				html += 'Response text: ' + js
		finally:
			con.close()
		return html

	def __str__(self):
		content_text = ''

		if self.friend.id == 1: # This is me
			content_text = Content.objects.get(pk=self.content).file_path
		else:
			content_text = 'The file is on another friend\'s computer'

		return "Link {0}: Content {1}".format(self.friend.name, content_text)