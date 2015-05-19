from django.conf.urls import patterns, include, url
from django.contrib import admin

import settings

urlpatterns = patterns('',
    
    # Front end
    url(r'^o2m/home$', 'basic_client.views.home'), #Displays your own content tree
    url(r'^o2m/timeline$', 'basic_client.views.timeline'), #Displays a timeline view of all of your friends/timelines
    url(r'^o2m/friend/(?P<friend_name>.*)$', 'basic_client.views.friend'), #Displays a timeline view of all of your friends/timelines
    url(r'^o2m/notifications$', 'basic_client.views.notifications'), #Displays a timeline view of all of your friends/timelines
    url(r'^o2m/add_content$', 'basic_client.views.add_content'), #Adds content to your server and a link to the friend specified
    url(r'^o2m/delete_content$', 'basic_client.views.delete_content'),
    url(r'^o2m/delete_link$', 'basic_client.views.delete_link'),
    # Back end

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
    url(r'^extra/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.EXTRA_ROOT,
    }),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^posts$', 'basic_server.views.posts'),
    url(r'^timeline$', 'basic_server.views.timeline'),
    url(r'^node/(?P<content_id>.*)$', 'basic_server.views.link'),
    url(r'^content/(?P<content_id>[0-9]*)$', 'basic_server.views.content'),
    url(r'^notifications/$', 'basic_server.views.notifications'),

)
