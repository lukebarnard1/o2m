from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from basic_server.models import Link, LinkEdge, Content

import o2m
import os
import json

def file_to_html(file_path):
	file_type = file_path[file_path.rindex('.') + 1:].lower()

	if file_type == 'txt':
		try:
			f = open(os.path.join(o2m.settings.MEDIA_ROOT,file_path[len(o2m.settings.MEDIA_URL):]), 'r')
		except IOError as e:
			return 'Failed to open file at ' + file_path
		try:
			text = f.read()

			return '<p>{0}</p>'.format(text)
		except IOError as e:
			return 'Failed to read text file at ' + file_path

	elif file_type == 'png' or file_type == 'jpg':
		return '<img src="{0}" width=200/>'.format(file_path)

	return 'Unknown file type'


def render_html(content, level = 1):
	html = ''

	# Not a link
	if 'children' in content.keys():
		html += file_to_html(content['file_path'])

		for child in content['children']:
			html += '<div style="margin-left:{0}px;">'.format(level*20) + render_html(child) + '</div>'
	else:
		html += '<a href="http://' + content['friend']['address'] + ':' + str(content['friend']['port']) + '/content/' + str(content['content']) + '">Link to ' + content['friend']['name'] + '/' + str(content['content']) + '</a>'
	return html

def render_json(content):
	js = json.dumps(content)
	return js


def file_path_to_media(file_path):
	return o2m.settings.MEDIA_URL + file_path[len(o2m.settings.O2M_BASE) + 1:]

def traverse_posts(link = 1, limit = 10):
	"""Starting from a particular link, traverse link edges, which
	are pairs of links until either there are no more child nodes
	to traverse or the recursion depth limit is met. Returns a
	dictionary containing links and content in the tree of links.
	Some content will not have any children. Others won't have a
	children list at all - these are links to friend's content.
	"""
	django_link = Link.objects.get(pk = link)
	django_content = django_link.get_content()

	if django_content:
		content = model_to_dict(django_content)

		content['creation_time'] = content['creation_time'].__str__()
		content['children'] = []
		content['file_path'] = file_path_to_media(content['file_path'])
		if limit > 1:

			link_edges = LinkEdge.objects.filter(a = link)
			
			if len(link_edges) > 0:
				for edge in link_edges:
					child = traverse_posts(edge.b, limit - 1)
					content['children'].append(child)
		return content
	else:
		link = model_to_dict(django_link)
		link['friend'] = model_to_dict(django_link.friend)
		return link

def render(format, content):
	if format == 'html':
		return render_html(content)
	elif format == 'json':
		return render_json(content)
	else:
		raise Exception('Format not supported')

def posts(request, markup):
	return content(request, 1, markup)

def content(request, id, markup):
	link = get_object_or_404(Link, content = id, friend = 1)

	if not markup: markup = 'html'

	root_link = traverse_posts(link.id)

	response = render(markup, root_link)

	return HttpResponse(response)
	# return HttpResponse(content_to_json(model_to_dict(Content.objects.get(pk = id))))
