from django.contrib import admin

from basic_server.models import Friend, Content, Link, LinkEdge

admin.site.register(Friend)
admin.site.register(Content)
admin.site.register(Link)
admin.site.register(LinkEdge)