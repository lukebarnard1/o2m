from django.db import models

# Create your models here.


class Friend(models.Model):
	name = models.CharField(max_length=128)
	address = models.IPAddressField()
	password = models.CharField(max_length=32)

class Content(models.Model):
	file_path = models.FilePathField()
	creation_time = models.DateTimeField()
	integer = models.IntegerField() # Non-descript to allow variations

class Link(models.Model):
	friend = models.ForeignKey(Friend) # (Could be yourself)
	content = models.BigIntegerField() # (Could be your own)
	next = models.BigIntegerField() # to the next link in the tree
