from django.conf.urls import patterns, include, url
from django.contrib import admin

import settings

urlpatterns = patterns('',
    
    # Front end
    url(r'^posts(\.(?P<markup>.*))?$', 'basic_server.views.posts'),

    # Back end
    url(r'^content/(?P<id>[0-9]*)(\.(?P<markup>.*))?$', 'basic_server.views.content'),


	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
	    'document_root': settings.MEDIA_ROOT,
	}),
    url(r'^admin/', include(admin.site.urls)),
)
