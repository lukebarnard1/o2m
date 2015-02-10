from django.db import models
import o2m.settings

# Create your models here.


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

	def __str__(self):
		return "Content {0}".format(self.id)

class Link(models.Model):
	friend = models.ForeignKey(Friend) # (Could be yourself)
	content = models.BigIntegerField() # (Could be your own)

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
			content_text = Content.objects.get(pk=self.content).file_path
		else:
			content_text = 'The file is on another friend\'s computer'

		return "Link {0}: Content {1}".format(self.friend.name, content_text)

class LinkEdge(models.Model):
	a = models.BigIntegerField() # Link
	b = models.BigIntegerField() # Next link

	def __str__(self):
		return "LinkEdge {0} to {1}".format(self.a, self.b)
