o2m = new Object();

o2m.update_friend = function (friend_id, data, callback) {
	if(!callback) {
		callback = function(response){console.log(response.status)}
	}
	
	$.ajax({
		url: '/friend/' + friend_id,
		type: 'PUT',
		success: callback,
		data: JSON.stringify(data),
		error: function(response){console.log(response.status)}
	})
}

o2m.set_my_user_photo = function (content) {
	function done(response) {
		window.location = '/o2m/timeline'
	}
	o2m.update_friend(o2m.me.id, {'photo_content_id':content.id}, done)
}

o2m.upload_new_display_picture = function () {
	this.select_content_form.select_content(this.set_my_user_photo, 'image/jpeg')
}