from django.conf.urls import patterns, include, url
from django.contrib import admin

import settings

urlpatterns = patterns('',
    
    # Front end
    url(r'^$', 'o2m.basic_client.views.timeline_view.timeline'),
    url(r'^o2m/login$', 'o2m.basic_client.views.login.login_view'),
    url(r'^o2m/home$', 'o2m.basic_client.views.timeline_view.home'), #Displays your own content tree
    url(r'^o2m/timeline$', 'o2m.basic_client.views.timeline_view.timeline'), #Displays a timeline view of all of your friends/timelines
    url(r'^o2m/friends', 'o2m.basic_client.views.friend.friend_list'), #Displays a timeline view of all of your friends/timelines
    url(r'^o2m/friend/(?P<friend_name>[^\@\:\/]*)$', 'o2m.basic_client.views.friend.friend'), #Displays a timeline view of all of your friends/timelines
    url(r'^o2m/non_friend/(?P<friend_name>.*)\@(?P<friend_ip>.*)\:(?P<friend_port>.*)$', 'o2m.basic_client.views.friend.friend'), #Displays a timeline view of all of your friends/timelines
    url(r'^o2m/friend/(?P<friend_name>[^\@\:\/]*)/content/(?P<content_id>[0-9]*)$', 'o2m.basic_client.views.friend.friend_content'), #Retrieves content from a friend
    url(r'^o2m/add_friend/(?P<friend_name>.*)\@(?P<friend_ip>.*)\:(?P<friend_port>.*)$', 'o2m.basic_client.views.friend.add_friend'), #Displays a timeline view of all of your friends/timelines
    url(r'^o2m/notifications$', 'o2m.basic_client.views.notifications.notifications'), #Displays a list of notifications
    
    url(r'^o2m/add_linked_content$', 'o2m.basic_client.views.add_linked_content'), #Adds content to your server and a link to the friend specified
    url(r'^o2m/delete_content$', 'o2m.basic_client.views.delete_content'),
    url(r'^o2m/delete_link$', 'o2m.basic_client.views.delete_link'),
    url(r'^o2m/username$', 'o2m.basic_client.views.username'),
    url(r'^o2m/login_user$', 'o2m.basic_client.views.login.login_user'),

    # Back end

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
    url(r'^extra/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.EXTRA_ROOT,
    }),
    url(r'^admin/', include(admin.site.urls)),
    url('^', include('django.contrib.auth.urls')),

    url(r'^posts$', 'o2m.basic_server.views.posts'),
    url(r'^timeline$', 'o2m.basic_server.views.timeline'),
    url(r'^node/(?P<content_id>.*)$', 'o2m.basic_server.views.link'),
    url(r'^content/(?P<content_id>[0-9]*)$', 'o2m.basic_server.views.content'),
    url(r'^content_list/(?P<mime_type>.+)$', 'o2m.basic_server.views.content_list'),
    url(r'^content_list$', 'o2m.basic_server.views.content_list'),
    url(r'^notifications/$', 'o2m.basic_server.views.notifications'),
    url(r'^friend/(?P<friend_id>[0-9]*)$', 'o2m.basic_server.views.friend'),

)
