
from django.http import HttpResponse
import o2m
from json_view import JSONView
from ..models import Link, Friend

class LinkView(JSONView):

	content_id = 1

	def must_be_owner(self, request):
		"""You must be owner to add a child link to the link
		that refers to content 1. Deletion authentication is
		handled in the delete method."""
		return request.method == 'POST' and self.content_id == 1

	def get_node_for_json(self):
		if self.content_id == 1:
			try:
				return Link.objects.filter()[0]
			except IndexError as e:
				return None
		else:
			return Link.objects.get(content=self.content_id)

	def notify_content_owners(self, me, node, friend_posting):
		"""Notify the owner of a node that someone has added
		content as a descendant of it."""

		node.friend.send_notification(me, notification_type='Reply to post', obj_id=node.id, obj_creator=friend_posting.name)

		if node.parent:
			self.notify_content_owners(me, node.parent, friend_posting)

	def post(self, request):
		"""Add a post based on the request.

		POST variables must include 'content_id' to assign the 
		ID of the related content, which may not be on the 
		same machine as the link.

		This method currently assumes that the content will be
		there."""
		potential_parents = Link.objects.filter(content = self.content_id)

		print '(Server)Adding link to first of ',potential_parents

		if len(potential_parents):
			parent = potential_parents[0]
		else:
			parent = None

		friend = Friend.objects.get(name = request.user.username)
		try:
			content = request.POST['content_id']

		except MultiValueDictKeyError as e:
			r = HttpResponse()
			r.status = 501
			r.reason = 'No content id specified'
			return r

		link = Link.objects.create(friend = friend, content = content)
		link.parent = parent
		link.save()

		me = Friend.objects.get(name=o2m.settings.ME)

		if parent:
			self.notify_content_owners(me, parent, friend)

		return HttpResponse('Link added')

	def delete(self, request):
		"""Delete a link from the tree and any links below it.

		This does not affect content."""

		link = Link.objects.get(content = self.content_id)

		friend = Friend.objects.get(name = request.user.username)
		
		if link.friend.id == friend.id:
			link.delete()
			return HttpResponse('Link deleted')
		else:
			r = HttpResponse()
			r.status = 403
			r.reason = 'You can only delete links that you created'
			return r