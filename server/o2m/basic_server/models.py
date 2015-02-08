from django.db import models

# Create your models here.

'''
MODEL ARCHITECTURE

Friend
	- Name
	- IP Address
	- Password

Content
	- Content local file name
	- Creation time
	- Integer: Non-descript to allow variations

Link
	- Friend (Could be yourself)
	- Content (Could be your own)
	- Link: to the previous link in the tree

'''