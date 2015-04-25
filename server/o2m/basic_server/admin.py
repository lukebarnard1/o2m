from django.contrib import admin

from basic_server.models import Friend, Content, Link, Notification, NotificationType

admin.site.register(Friend)
admin.site.register(Content)
admin.site.register(Notification)
admin.site.register(NotificationType)
# admin.site.register(Link)

from django_mptt_admin.admin import DjangoMpttAdmin

class LinkAdmin(DjangoMpttAdmin):
	pass

admin.site.register(Link, LinkAdmin)